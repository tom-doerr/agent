#!/usr/bin/env python3
"""Security and performance monitoring dashboard for agents."""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import pandas as pd


class SecurityDashboard:
    """Analyze and visualize agent security metrics."""
    
    def __init__(self, data_dir: Path = Path(".")):
        self.data_dir = data_dir
        self.audit_data = []
        self.token_data = []
        self.context_data = []
        
    def load_audit_logs(self, pattern: str = "**/command_audit.ndjson"):
        """Load command audit logs."""
        self.audit_data = []
        for audit_file in self.data_dir.glob(pattern):
            with open(audit_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry['source_file'] = str(audit_file)
                        self.audit_data.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        print(f"Loaded {len(self.audit_data)} audit entries")
        
    def load_token_logs(self, pattern: str = "**/token_usage.ndjson"):
        """Load token usage logs."""
        self.token_data = []
        for token_file in self.data_dir.glob(pattern):
            with open(token_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry['source_file'] = str(token_file)
                        self.token_data.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        print(f"Loaded {len(self.token_data)} token entries")
    
    def analyze_security_metrics(self) -> Dict[str, Any]:
        """Analyze security-related metrics."""
        if not self.audit_data:
            return {}
        
        # Command statistics
        total_commands = len(self.audit_data)
        status_counts = Counter(entry['status'] for entry in self.audit_data)
        
        # Blocked commands analysis
        blocked_commands = [
            entry for entry in self.audit_data 
            if entry['status'] == 'blocked'
        ]
        blocked_patterns = Counter(
            entry['command'].split()[0] if entry.get('command') else 'unknown'
            for entry in blocked_commands
        )
        
        # Timeout analysis
        timeouts = [
            entry for entry in self.audit_data 
            if entry['status'] == 'timeout'
        ]
        
        # Performance metrics
        durations = [
            entry['duration_seconds'] 
            for entry in self.audit_data 
            if 'duration_seconds' in entry and entry['duration_seconds'] is not None
        ]
        
        # Time-based analysis
        hourly_commands = defaultdict(int)
        daily_blocks = defaultdict(int)
        
        for entry in self.audit_data:
            if 'timestamp' in entry:
                try:
                    dt = datetime.fromisoformat(entry['timestamp'])
                    hourly_commands[dt.hour] += 1
                    if entry['status'] == 'blocked':
                        daily_blocks[dt.date()] += 1
                except:
                    continue
        
        return {
            'total_commands': total_commands,
            'status_counts': dict(status_counts),
            'blocked_rate': status_counts['blocked'] / total_commands if total_commands > 0 else 0,
            'success_rate': status_counts['success'] / total_commands if total_commands > 0 else 0,
            'timeout_rate': status_counts['timeout'] / total_commands if total_commands > 0 else 0,
            'blocked_patterns': dict(blocked_patterns.most_common(10)),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'hourly_distribution': dict(hourly_commands),
            'daily_blocks': dict(daily_blocks),
        }
    
    def plot_security_dashboard(self, save_path: str = "security_dashboard.png"):
        """Create comprehensive security dashboard visualization."""
        metrics = self.analyze_security_metrics()
        
        if not metrics:
            print("No data to visualize")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        fig.suptitle('Agent Security Dashboard', fontsize=16)
        
        # 1. Command Status Distribution
        ax = axes[0, 0]
        if 'status_counts' in metrics:
            statuses = list(metrics['status_counts'].keys())
            counts = list(metrics['status_counts'].values())
            colors = ['green' if s == 'success' else 'red' if s == 'blocked' else 'orange' for s in statuses]
            ax.bar(statuses, counts, color=colors)
            ax.set_title('Command Status Distribution')
            ax.set_ylabel('Count')
            
            # Add percentage labels
            total = sum(counts)
            for i, (status, count) in enumerate(zip(statuses, counts)):
                ax.text(i, count + 1, f'{count/total*100:.1f}%', ha='center')
        
        # 2. Blocked Commands
        ax = axes[0, 1]
        if 'blocked_patterns' in metrics and metrics['blocked_patterns']:
            commands = list(metrics['blocked_patterns'].keys())[:10]
            counts = list(metrics['blocked_patterns'].values())[:10]
            ax.barh(commands, counts, color='red')
            ax.set_title('Top Blocked Commands')
            ax.set_xlabel('Block Count')
        
        # 3. Hourly Activity
        ax = axes[0, 2]
        if 'hourly_distribution' in metrics:
            hours = list(range(24))
            counts = [metrics['hourly_distribution'].get(h, 0) for h in hours]
            ax.plot(hours, counts, marker='o')
            ax.set_title('Commands by Hour of Day')
            ax.set_xlabel('Hour')
            ax.set_ylabel('Command Count')
            ax.set_xticks(range(0, 24, 4))
        
        # 4. Security Metrics
        ax = axes[1, 0]
        security_metrics = {
            'Block Rate': metrics.get('blocked_rate', 0) * 100,
            'Success Rate': metrics.get('success_rate', 0) * 100,
            'Timeout Rate': metrics.get('timeout_rate', 0) * 100,
        }
        
        bars = ax.bar(security_metrics.keys(), security_metrics.values())
        ax.set_title('Security Metrics (%)')
        ax.set_ylabel('Percentage')
        ax.set_ylim(0, 100)
        
        # Color bars based on thresholds
        for bar, (metric, value) in zip(bars, security_metrics.items()):
            if metric == 'Block Rate':
                bar.set_color('red' if value > 20 else 'orange' if value > 10 else 'green')
            elif metric == 'Success Rate':
                bar.set_color('green' if value > 80 else 'orange' if value > 60 else 'red')
            elif metric == 'Timeout Rate':
                bar.set_color('red' if value > 10 else 'orange' if value > 5 else 'green')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}%', ha='center', va='bottom')
        
        # 5. Command Duration Distribution
        ax = axes[1, 1]
        if self.audit_data:
            durations = [
                entry['duration_seconds'] 
                for entry in self.audit_data 
                if 'duration_seconds' in entry and entry['duration_seconds'] is not None
            ]
            if durations:
                ax.hist(durations, bins=30, color='blue', alpha=0.7)
                ax.set_title('Command Duration Distribution')
                ax.set_xlabel('Duration (seconds)')
                ax.set_ylabel('Count')
                ax.axvline(metrics['avg_duration'], color='red', 
                          linestyle='--', label=f'Avg: {metrics["avg_duration"]:.2f}s')
                ax.legend()
        
        # 6. Daily Block Trends
        ax = axes[1, 2]
        if 'daily_blocks' in metrics and metrics['daily_blocks']:
            dates = sorted(metrics['daily_blocks'].keys())
            counts = [metrics['daily_blocks'][d] for d in dates]
            
            # Convert to pandas for better date handling
            df = pd.DataFrame({'date': dates, 'blocks': counts})
            ax.plot(df['date'], df['blocks'], marker='o', color='red')
            ax.set_title('Daily Blocked Commands')
            ax.set_xlabel('Date')
            ax.set_ylabel('Blocked Count')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Dashboard saved to {save_path}")
        
        # Also save metrics as JSON
        metrics_path = save_path.replace('.png', '_metrics.json')
        with open(metrics_path, 'w') as f:
            # Convert date objects to strings for JSON serialization
            json_safe_metrics = {}
            for k, v in metrics.items():
                if k == 'daily_blocks':
                    json_safe_metrics[k] = {str(date): count for date, count in v.items()}
                else:
                    json_safe_metrics[k] = v
            json.dump(json_safe_metrics, f, indent=2)
        print(f"Metrics saved to {metrics_path}")
    
    def generate_security_report(self) -> str:
        """Generate a text security report."""
        metrics = self.analyze_security_metrics()
        
        if not metrics:
            return "No security data available"
        
        report = []
        report.append("=" * 60)
        report.append("AGENT SECURITY REPORT")
        report.append("=" * 60)
        report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary Statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 30)
        report.append(f"Total Commands Executed: {metrics['total_commands']}")
        report.append(f"Successful Commands: {metrics['status_counts'].get('success', 0)}")
        report.append(f"Blocked Commands: {metrics['status_counts'].get('blocked', 0)}")
        report.append(f"Timed Out Commands: {metrics['status_counts'].get('timeout', 0)}")
        report.append(f"Failed Commands: {metrics['status_counts'].get('failed', 0)}")
        report.append("")
        
        # Security Metrics
        report.append("SECURITY METRICS")
        report.append("-" * 30)
        report.append(f"Command Block Rate: {metrics['blocked_rate']*100:.1f}%")
        report.append(f"Command Success Rate: {metrics['success_rate']*100:.1f}%")
        report.append(f"Command Timeout Rate: {metrics['timeout_rate']*100:.1f}%")
        report.append("")
        
        # Risk Assessment
        report.append("RISK ASSESSMENT")
        report.append("-" * 30)
        
        if metrics['blocked_rate'] > 0.2:
            report.append("⚠️  HIGH RISK: Block rate exceeds 20%")
        elif metrics['blocked_rate'] > 0.1:
            report.append("⚠️  MEDIUM RISK: Block rate exceeds 10%")
        else:
            report.append("✅ LOW RISK: Block rate within acceptable range")
        
        if metrics['timeout_rate'] > 0.1:
            report.append("⚠️  WARNING: High timeout rate may indicate resource attacks")
        
        report.append("")
        
        # Most Blocked Commands
        if metrics['blocked_patterns']:
            report.append("TOP BLOCKED COMMANDS")
            report.append("-" * 30)
            for cmd, count in list(metrics['blocked_patterns'].items())[:5]:
                report.append(f"  {cmd}: {count} attempts")
            report.append("")
        
        # Performance Statistics
        report.append("PERFORMANCE STATISTICS")
        report.append("-" * 30)
        report.append(f"Average Command Duration: {metrics['avg_duration']:.2f} seconds")
        report.append(f"Maximum Command Duration: {metrics['max_duration']:.2f} seconds")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 30)
        
        if metrics['blocked_rate'] > 0.1:
            report.append("• Review blocked commands and consider security training")
            report.append("• Verify command whitelist is appropriate for use case")
        
        if metrics['timeout_rate'] > 0.05:
            report.append("• Investigate timeout causes")
            report.append("• Consider adjusting resource limits")
        
        if metrics['avg_duration'] > 5:
            report.append("• Long average duration may impact user experience")
            report.append("• Consider optimizing command execution")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description='Security monitoring dashboard for agents')
    parser.add_argument(
        '--data-dir', type=str, default='.',
        help='Directory containing agent data files'
    )
    parser.add_argument(
        '--output', type=str, default='security_dashboard.png',
        help='Output path for dashboard image'
    )
    parser.add_argument(
        '--report', action='store_true',
        help='Generate text report instead of visualization'
    )
    
    args = parser.parse_args()
    
    dashboard = SecurityDashboard(Path(args.data_dir))
    dashboard.load_audit_logs()
    dashboard.load_token_logs()
    
    if args.report:
        report = dashboard.generate_security_report()
        print(report)
        
        # Save report to file
        report_path = args.output.replace('.png', '.txt')
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\nReport saved to {report_path}")
    else:
        dashboard.plot_security_dashboard(args.output)


if __name__ == "__main__":
    main()