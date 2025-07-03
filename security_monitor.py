#!/usr/bin/env python3
"""
Real-time security monitor for running agents.
Watches audit logs and alerts on suspicious activity.
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
import argparse
from dataclasses import dataclass
import sys

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("Please install rich: pip install rich")
    sys.exit(1)


@dataclass
class SecurityAlert:
    """Represents a security alert."""
    timestamp: datetime
    severity: str  # 'critical', 'high', 'medium', 'low'
    alert_type: str
    message: str
    details: Dict[str, Any]
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'type': self.alert_type,
            'message': self.message,
            'details': self.details,
        }


class SecurityMonitor:
    """Real-time security monitoring for agents."""
    
    def __init__(self, watch_dir: Path = Path("."), alert_threshold: Dict[str, int] = None):
        self.watch_dir = watch_dir
        self.console = Console()
        self.running = False
        
        # Alert thresholds
        self.alert_threshold = alert_threshold or {
            'blocked_commands_per_minute': 5,
            'failed_commands_per_minute': 10,
            'timeout_commands_per_minute': 3,
            'total_commands_per_minute': 100,
            'suspicious_pattern_count': 3,
        }
        
        # Monitoring state
        self.audit_files = {}  # file -> last position
        self.recent_commands = deque(maxlen=1000)
        self.alerts = deque(maxlen=100)
        self.stats = defaultdict(int)
        self.command_history = defaultdict(lambda: deque(maxlen=60))  # 60 seconds of history
        
        # Suspicious patterns
        self.suspicious_patterns = [
            'rm -rf',
            'base64',
            'curl.*\\|.*sh',  # curl pipe to shell
            'wget.*\\|.*sh',
            '/etc/passwd',
            '/etc/shadow',
            'sudo',
            'chmod 777',
            'nc -e',  # netcat with execute
            'python -c.*import.*os',
            'eval\\(',
            'exec\\(',
        ]
    
    def start_monitoring(self):
        """Start the monitoring threads."""
        self.running = True
        
        # Start file watcher thread
        watcher_thread = threading.Thread(target=self._watch_audit_files, daemon=True)
        watcher_thread.start()
        
        # Start analyzer thread
        analyzer_thread = threading.Thread(target=self._analyze_commands, daemon=True)
        analyzer_thread.start()
        
        # Start UI
        self._run_ui()
    
    def _watch_audit_files(self):
        """Watch audit files for new entries."""
        while self.running:
            try:
                # Find all audit files
                for audit_file in self.watch_dir.rglob("**/command_audit.ndjson"):
                    self._process_audit_file(audit_file)
                
                time.sleep(0.5)  # Check every 500ms
            except Exception as e:
                self.console.print(f"[red]Watcher error: {e}[/red]")
    
    def _process_audit_file(self, file_path: Path):
        """Process new entries in an audit file."""
        try:
            # Get last read position
            last_pos = self.audit_files.get(str(file_path), 0)
            
            with open(file_path, 'r') as f:
                f.seek(last_pos)
                
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        self._process_audit_entry(entry)
                    except json.JSONDecodeError:
                        continue
                
                # Update position
                self.audit_files[str(file_path)] = f.tell()
                
        except Exception as e:
            pass  # File might be temporarily unavailable
    
    def _process_audit_entry(self, entry: Dict[str, Any]):
        """Process a single audit entry."""
        # Add to recent commands
        self.recent_commands.append(entry)
        
        # Update stats
        self.stats['total_commands'] += 1
        self.stats[f"status_{entry.get('status', 'unknown')}"] += 1
        
        # Add to time-based history
        timestamp = datetime.fromisoformat(entry['timestamp'])
        self.command_history[timestamp.minute].append(entry)
        
        # Check for immediate alerts
        if entry.get('status') == 'blocked':
            self._check_blocked_command(entry)
        
        if entry.get('status') == 'timeout':
            self._check_timeout_command(entry)
    
    def _analyze_commands(self):
        """Analyze commands for security issues."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Count commands in last minute
                one_minute_ago = current_time - timedelta(minutes=1)
                recent_minute_commands = [
                    cmd for cmd in self.recent_commands
                    if datetime.fromisoformat(cmd['timestamp']) > one_minute_ago
                ]
                
                # Check rate limits
                self._check_command_rates(recent_minute_commands)
                
                # Check for suspicious patterns
                self._check_suspicious_patterns(recent_minute_commands)
                
                # Clean old history
                old_minute = (current_time.minute - 2) % 60
                if old_minute in self.command_history:
                    del self.command_history[old_minute]
                
                time.sleep(5)  # Analyze every 5 seconds
                
            except Exception as e:
                self.console.print(f"[red]Analyzer error: {e}[/red]")
    
    def _check_blocked_command(self, entry: Dict[str, Any]):
        """Check blocked command for security issues."""
        command = entry.get('command', '')
        
        # Check if it's a known attack pattern
        for pattern in self.suspicious_patterns:
            if pattern in command.lower():
                self._add_alert(
                    severity='high',
                    alert_type='blocked_attack_pattern',
                    message=f"Blocked command matches attack pattern: {pattern}",
                    details={'command': command, 'pattern': pattern}
                )
                break
    
    def _check_timeout_command(self, entry: Dict[str, Any]):
        """Check timeout command for resource exhaustion."""
        command = entry.get('command', '')
        duration = entry.get('duration_seconds', 0)
        
        if duration > 30:
            self._add_alert(
                severity='medium',
                alert_type='long_running_command',
                message=f"Command ran for {duration:.1f} seconds before timeout",
                details={'command': command, 'duration': duration}
            )
    
    def _check_command_rates(self, recent_commands: List[Dict]):
        """Check command execution rates."""
        if not recent_commands:
            return
        
        # Count by status
        status_counts = defaultdict(int)
        for cmd in recent_commands:
            status_counts[cmd.get('status', 'unknown')] += 1
        
        # Check thresholds
        if status_counts['blocked'] > self.alert_threshold['blocked_commands_per_minute']:
            self._add_alert(
                severity='high',
                alert_type='high_block_rate',
                message=f"High block rate: {status_counts['blocked']} commands blocked in last minute",
                details={'blocked_count': status_counts['blocked']}
            )
        
        if status_counts['failed'] > self.alert_threshold['failed_commands_per_minute']:
            self._add_alert(
                severity='medium',
                alert_type='high_failure_rate',
                message=f"High failure rate: {status_counts['failed']} commands failed in last minute",
                details={'failed_count': status_counts['failed']}
            )
        
        total = len(recent_commands)
        if total > self.alert_threshold['total_commands_per_minute']:
            self._add_alert(
                severity='medium',
                alert_type='high_command_rate',
                message=f"Unusually high command rate: {total} commands in last minute",
                details={'total_count': total}
            )
    
    def _check_suspicious_patterns(self, recent_commands: List[Dict]):
        """Check for suspicious command patterns."""
        pattern_counts = defaultdict(int)
        
        for cmd in recent_commands:
            command = cmd.get('command', '').lower()
            for pattern in self.suspicious_patterns:
                if pattern in command:
                    pattern_counts[pattern] += 1
        
        # Alert on repeated suspicious patterns
        for pattern, count in pattern_counts.items():
            if count >= self.alert_threshold['suspicious_pattern_count']:
                self._add_alert(
                    severity='critical',
                    alert_type='repeated_suspicious_pattern',
                    message=f"Suspicious pattern '{pattern}' seen {count} times in last minute",
                    details={'pattern': pattern, 'count': count}
                )
    
    def _add_alert(self, severity: str, alert_type: str, message: str, details: Dict):
        """Add a security alert."""
        alert = SecurityAlert(
            timestamp=datetime.now(),
            severity=severity,
            alert_type=alert_type,
            message=message,
            details=details
        )
        
        self.alerts.append(alert)
        self.stats[f'alerts_{severity}'] += 1
        
        # Log critical alerts immediately
        if severity == 'critical':
            self.console.print(f"\n[bold red]🚨 CRITICAL ALERT: {message}[/bold red]\n")
    
    def _run_ui(self):
        """Run the monitoring UI."""
        layout = self._create_layout()
        
        with Live(layout, refresh_per_second=2, screen=True) as live:
            while self.running:
                try:
                    # Update layout sections
                    layout["header"].update(self._create_header())
                    layout["stats"].update(self._create_stats_panel())
                    layout["alerts"].update(self._create_alerts_panel())
                    layout["commands"].update(self._create_commands_panel())
                    
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    self.running = False
                    break
    
    def _create_layout(self) -> Layout:
        """Create the UI layout."""
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        
        layout["left"].split(
            Layout(name="stats", size=10),
            Layout(name="alerts"),
        )
        
        layout["right"].update(Layout(name="commands"))
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create header panel."""
        return Panel(
            Text("🔒 Agent Security Monitor", style="bold blue", justify="center"),
            border_style="blue",
        )
    
    def _create_stats_panel(self) -> Panel:
        """Create statistics panel."""
        table = Table(show_header=False, box=None)
        
        # Add stats
        table.add_row("Total Commands:", str(self.stats['total_commands']))
        table.add_row("Successful:", f"[green]{self.stats.get('status_success', 0)}[/green]")
        table.add_row("Blocked:", f"[red]{self.stats.get('status_blocked', 0)}[/red]")
        table.add_row("Failed:", f"[yellow]{self.stats.get('status_failed', 0)}[/yellow]")
        table.add_row("Timeouts:", f"[orange1]{self.stats.get('status_timeout', 0)}[/orange1]")
        
        # Alert counts
        table.add_row("", "")  # Spacer
        table.add_row("Critical Alerts:", f"[red]{self.stats.get('alerts_critical', 0)}[/red]")
        table.add_row("High Alerts:", f"[orange1]{self.stats.get('alerts_high', 0)}[/orange1]")
        table.add_row("Medium Alerts:", f"[yellow]{self.stats.get('alerts_medium', 0)}[/yellow]")
        
        return Panel(table, title="Statistics", border_style="green")
    
    def _create_alerts_panel(self) -> Panel:
        """Create alerts panel."""
        if not self.alerts:
            content = Text("No alerts yet", style="dim")
        else:
            lines = []
            for alert in list(self.alerts)[-10:]:  # Last 10 alerts
                time_str = alert.timestamp.strftime("%H:%M:%S")
                severity_style = {
                    'critical': 'bold red',
                    'high': 'orange1',
                    'medium': 'yellow',
                    'low': 'green'
                }.get(alert.severity, 'white')
                
                lines.append(
                    f"[{severity_style}]{time_str} [{alert.severity.upper()}][/{severity_style}] "
                    f"{alert.message}"
                )
            
            content = Text("\n".join(lines))
        
        return Panel(content, title="Recent Alerts", border_style="red")
    
    def _create_commands_panel(self) -> Panel:
        """Create recent commands panel."""
        if not self.recent_commands:
            content = Text("No commands yet", style="dim")
        else:
            lines = []
            for cmd in list(self.recent_commands)[-15:]:  # Last 15 commands
                timestamp = datetime.fromisoformat(cmd['timestamp'])
                time_str = timestamp.strftime("%H:%M:%S")
                status = cmd.get('status', 'unknown')
                
                status_style = {
                    'success': 'green',
                    'blocked': 'red',
                    'failed': 'yellow',
                    'timeout': 'orange1'
                }.get(status, 'white')
                
                command = cmd.get('command', '')[:50] + '...' if len(cmd.get('command', '')) > 50 else cmd.get('command', '')
                
                lines.append(
                    f"{time_str} [{status_style}]{status:8}[/{status_style}] {command}"
                )
            
            content = Text("\n".join(lines))
        
        return Panel(content, title="Recent Commands", border_style="blue")
    
    def save_alerts(self, output_file: str):
        """Save alerts to file."""
        alerts_data = [alert.to_dict() for alert in self.alerts]
        with open(output_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Real-time security monitor for agents')
    parser.add_argument(
        '--watch-dir', type=str, default='.',
        help='Directory to watch for audit files'
    )
    parser.add_argument(
        '--block-threshold', type=int, default=5,
        help='Alert threshold for blocked commands per minute'
    )
    parser.add_argument(
        '--save-alerts', type=str,
        help='Save alerts to file on exit'
    )
    
    args = parser.parse_args()
    
    # Configure thresholds
    thresholds = {
        'blocked_commands_per_minute': args.block_threshold,
        'failed_commands_per_minute': 10,
        'timeout_commands_per_minute': 3,
        'total_commands_per_minute': 100,
        'suspicious_pattern_count': 3,
    }
    
    monitor = SecurityMonitor(
        watch_dir=Path(args.watch_dir),
        alert_threshold=thresholds
    )
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        
        if args.save_alerts:
            monitor.save_alerts(args.save_alerts)
            print(f"Alerts saved to {args.save_alerts}")


if __name__ == "__main__":
    main()