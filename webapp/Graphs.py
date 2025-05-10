import numpy as np
import matplotlib.pyplot as plt
import os


def viewg(g1, picname="default.png", name="Data"):
    # Data preparation
    bars = list(g1.keys())
    height = list(g1.values())
    y_pos = np.arange(len(bars))

    # Create the plot
    plt.figure(figsize=(10, 6))
    barlist = plt.bar(y_pos, height, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(bars))), edgecolor='black')

    # Add value labels on top of bars
    for i, v in enumerate(height):
        plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Styling the plot
    plt.xticks(y_pos, bars, fontsize=10)
    plt.ylabel('Value', fontsize=12)
    plt.title(f'{name} Graph', fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the figure
    output_path = os.path.join('D:\\Django\\CareerPath\\webapp\\static\\assets\\images', picname)
    plt.tight_layout()
    plt.savefig(output_path, )
    plt.clf()


# Example usage
if __name__ == "__main__":
    sample_data = {'Jan': 10, 'Feb': 25, 'Mar': 18, 'Apr': 30, 'May': 12}
    viewg(sample_data, "sample_graph.png", "Monthly Stats")
