#!/usr/bin/env python3
"""Plot token usage from optimization runs."""

import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import argparse
from datetime import datetime
import numpy as np


def load_token_log(filepath="token_usage.ndjson"):
    """Load token usage log."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue
    return pd.DataFrame(data)


def plot_token_usage(df, output_file="token_usage_plot.png"):
    """Create comprehensive token usage plots."""
    # Check if we have cost data
    has_cost = 'total_cost_usd' in df.columns and df['total_cost_usd'].notna().any()
    
    if has_cost:
        fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    else:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    fig.suptitle('Token Usage & Cost Analysis', fontsize=16)
    
    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'])
    
    # Plot 1: Cumulative tokens over time
    ax1 = axes[0, 0]
    df['cumulative_total'] = df['total_tokens'].cumsum()
    df['cumulative_input'] = df['input_tokens'].cumsum()
    df['cumulative_output'] = df['output_tokens'].cumsum()
    df['cumulative_reasoning'] = df['reasoning_tokens'].cumsum()
    
    ax1.plot(df['elapsed_seconds'], df['cumulative_total'], label='Total', linewidth=2)
    ax1.plot(df['elapsed_seconds'], df['cumulative_input'], label='Input', alpha=0.7)
    ax1.plot(df['elapsed_seconds'], df['cumulative_output'], label='Output', alpha=0.7)
    ax1.plot(df['elapsed_seconds'], df['cumulative_reasoning'], label='Reasoning', alpha=0.7)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Cumulative Tokens')
    ax1.set_title('Cumulative Token Usage Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Token usage per call
    ax2 = axes[0, 1]
    ax2.scatter(df['step'], df['total_tokens'], alpha=0.6, s=50)
    ax2.set_xlabel('Call Number')
    ax2.set_ylabel('Tokens per Call')
    ax2.set_title('Token Usage per LM Call')
    ax2.grid(True, alpha=0.3)
    
    # Add rolling average
    window = min(10, len(df) // 4)
    if window > 1:
        rolling_avg = df['total_tokens'].rolling(window=window, center=True).mean()
        ax2.plot(df['step'], rolling_avg, color='red', linewidth=2, label=f'{window}-call moving avg')
        ax2.legend()
    
    # Plot 3: Token composition
    ax3 = axes[1, 0]
    token_types = ['input_tokens', 'output_tokens', 'reasoning_tokens']
    token_sums = [df[t].sum() for t in token_types]
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    
    ax3.pie(token_sums, labels=['Input', 'Output', 'Reasoning'], colors=colors, autopct='%1.1f%%')
    ax3.set_title('Token Distribution by Type')
    
    # Plot 4: Phase analysis
    ax4 = axes[1, 1]
    phase_tokens = df.groupby('phase')['total_tokens'].agg(['sum', 'count', 'mean'])
    phases = phase_tokens.index
    x = np.arange(len(phases))
    
    bars = ax4.bar(x, phase_tokens['sum'])
    ax4.set_xlabel('Phase')
    ax4.set_ylabel('Total Tokens')
    ax4.set_title('Token Usage by Phase')
    ax4.set_xticks(x)
    ax4.set_xticklabels(phases, rotation=45, ha='right')
    
    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, phase_tokens['count'])):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}\n({count} calls)',
                ha='center', va='bottom', fontsize=9)
    
    ax4.grid(True, alpha=0.3, axis='y')
    
    # If we have cost data, add cost analysis plots
    if has_cost:
        # Plot 5: Cost per call over time
        ax5 = axes[2, 0]
        ax5.scatter(df['step'], df['total_cost_usd'], alpha=0.6, s=50, c='green')
        ax5.set_xlabel('Call Number')
        ax5.set_ylabel('Cost (USD)')
        ax5.set_title('Cost per LM Call')
        ax5.grid(True, alpha=0.3)
        
        # Add cumulative cost line
        df['cumulative_cost'] = df['total_cost_usd'].cumsum()
        ax5_twin = ax5.twinx()
        ax5_twin.plot(df['step'], df['cumulative_cost'], color='red', linewidth=2, label='Cumulative')
        ax5_twin.set_ylabel('Cumulative Cost (USD)', color='red')
        ax5_twin.tick_params(axis='y', labelcolor='red')
        
        # Plot 6: Cost-efficiency metric (tokens per dollar)
        ax6 = axes[2, 1]
        df['tokens_per_dollar'] = df['total_tokens'] / (df['total_cost_usd'] + 0.0001)  # Avoid division by zero
        ax6.scatter(df['step'], df['tokens_per_dollar'], alpha=0.6, s=50, c='purple')
        ax6.set_xlabel('Call Number')
        ax6.set_ylabel('Tokens per Dollar')
        ax6.set_title('Cost Efficiency Over Time')
        ax6.grid(True, alpha=0.3)
        
        # Add pricing period indicator
        if 'pricing_period' in df.columns:
            discount_mask = df['pricing_period'] == 'discount'
            if discount_mask.any():
                for ax in [ax5, ax6]:
                    for idx in df[discount_mask].index:
                        ax.axvspan(idx-0.5, idx+0.5, alpha=0.1, color='green')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    # Print statistics
    print("\n" + "="*60)
    print("TOKEN USAGE STATISTICS")
    print("="*60)
    print(f"Total calls: {len(df)}")
    print(f"Total tokens: {df['total_tokens'].sum():,}")
    print(f"Average tokens per call: {df['total_tokens'].mean():.1f}")
    print(f"Max tokens in single call: {df['total_tokens'].max():,}")
    print(f"Total duration: {df['elapsed_seconds'].max():.1f} seconds")
    
    if has_cost:
        print(f"\n💰 COST STATISTICS:")
        print(f"Total cost: ${df['total_cost_usd'].sum():.4f}")
        print(f"Average cost per call: ${df['total_cost_usd'].mean():.4f}")
        print(f"Min/Max cost per call: ${df['total_cost_usd'].min():.4f} - ${df['total_cost_usd'].max():.4f}")
        
        if 'pricing_period' in df.columns:
            for period in df['pricing_period'].unique():
                period_df = df[df['pricing_period'] == period]
                if len(period_df) > 0:
                    print(f"\n{period.capitalize()} period:")
                    print(f"  Calls: {len(period_df)}")
                    print(f"  Total cost: ${period_df['total_cost_usd'].sum():.4f}")
                    print(f"  Avg cost/call: ${period_df['total_cost_usd'].mean():.4f}")
    
    if 'optimizer' in df.columns:
        print("\nBy Optimizer:")
        for opt in df['optimizer'].unique():
            opt_df = df[df['optimizer'] == opt]
            cost_str = f" (${opt_df['total_cost_usd'].sum():.4f})" if has_cost else ""
            print(f"  {opt}: {opt_df['total_tokens'].sum():,} tokens{cost_str} in {len(opt_df)} calls")


def plot_comparison(log_files, output_file="token_comparison.png"):
    """Compare token usage across multiple optimization runs."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Token Usage Comparison Across Runs', fontsize=16)
    
    summaries = []
    for log_file in log_files:
        df = load_token_log(log_file)
        if 'optimizer' in df.columns:
            optimizer = df['optimizer'].iloc[0]
        else:
            optimizer = Path(log_file).stem
        
        summaries.append({
            'file': log_file,
            'optimizer': optimizer,
            'total_tokens': df['total_tokens'].sum(),
            'total_calls': len(df),
            'avg_tokens': df['total_tokens'].mean(),
            'duration': df['elapsed_seconds'].max() if 'elapsed_seconds' in df else 0
        })
    
    summary_df = pd.DataFrame(summaries)
    
    # Plot 1: Total tokens comparison
    x = np.arange(len(summary_df))
    bars1 = ax1.bar(x, summary_df['total_tokens'])
    ax1.set_xlabel('Run')
    ax1.set_ylabel('Total Tokens')
    ax1.set_title('Total Token Usage')
    ax1.set_xticks(x)
    ax1.set_xticklabels(summary_df['optimizer'], rotation=45, ha='right')
    
    for bar, val in zip(bars1, summary_df['total_tokens']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val):,}',
                ha='center', va='bottom')
    
    # Plot 2: Efficiency (tokens per second)
    efficiency = summary_df['total_tokens'] / summary_df['duration'].replace(0, 1)
    bars2 = ax2.bar(x, efficiency)
    ax2.set_xlabel('Run')
    ax2.set_ylabel('Tokens per Second')
    ax2.set_title('Token Processing Rate')
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary_df['optimizer'], rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Comparison plot saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Plot token usage from optimization runs')
    parser.add_argument('--log', default='token_usage.ndjson', help='Token log file')
    parser.add_argument('--output', default='token_usage_plot.png', help='Output plot file')
    parser.add_argument('--compare', nargs='+', help='Compare multiple log files')
    
    args = parser.parse_args()
    
    if args.compare:
        plot_comparison(args.compare, args.output)
    else:
        df = load_token_log(args.log)
        if len(df) == 0:
            print("No data found in log file")
            return
        
        plot_token_usage(df, args.output)


if __name__ == "__main__":
    main()