from graphviz import Digraph
from collections import defaultdict
import csv
import sys
import os
from pathlib import Path
from palettable.cartocolors.qualitative import Safe_10, Bold_10, Vivid_10
from palettable.colorbrewer.qualitative import Pastel1_9, Pastel2_8, Set1_9, Set2_8
import colorsys

def get_palette(mode, n):
    """
    Get a palette appropriate for the mode.

    Args:
        mode: 'light' or 'dark'
        n: number of colors needed

    Returns:
        List of hex color strings
    """
    if mode == 'light':
        # Light mode: pastel colors with black text
        palettes = [
            Pastel1_9.mpl_colors,
            Pastel2_8.mpl_colors,
            Set1_9.mpl_colors,
            Set2_8.mpl_colors,
        ]
    else:  # dark mode
        # Dark mode: bright/vibrant colors with white text
        palettes = [
            Bold_10.mpl_colors,
            Vivid_10.mpl_colors,
            Safe_10.mpl_colors,
        ]

    # Flatten all colors from palettes
    all_colors = []
    for palette in palettes:
        for color in palette:
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(color[0] * 255),
                int(color[1] * 255),
                int(color[2] * 255)
            )
            all_colors.append(hex_color)

    # If we need more colors than available, generate them
    if n > len(all_colors):
        print(f"Warning: Only {len(all_colors)} colors available in {mode} mode, "
              f"but {n} needed. Generating additional colors.")

        # Generate additional colors using HSV
        additional_needed = n - len(all_colors)
        for i in range(additional_needed):
            hue = i / additional_needed
            if mode == 'light':
                # Light mode: high lightness, moderate saturation
                rgb = colorsys.hls_to_rgb(hue, 0.8, 0.4)
            else:
                # Dark mode: moderate lightness, high saturation
                rgb = colorsys.hls_to_rgb(hue, 0.5, 0.8)

            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            all_colors.append(hex_color)

    return all_colors[:n]

def process_directory(data_dir):
    """Process a single directory and generate both light and dark mode graphs."""

    node_path = data_dir / 'node.csv'
    edge_path = data_dir / 'edge.csv'
    category_path = data_dir / 'category.csv'

    # Check if all required files exist
    if not node_path.exists():
        print(f"Error: {node_path} not found")
        sys.exit(1)
    if not edge_path.exists():
        print(f"Error: {edge_path} not found")
        sys.exit(1)
    if not category_path.exists():
        print(f"Error: {category_path} not found")
        sys.exit(1)

    # Read nodes
    nodes = []
    with open(node_path, 'r') as f:
        for node, in csv.reader(f):
            nodes.append(node)

    # Read categories and build mapping
    node_categories = defaultdict(set)
    with open(category_path, 'r') as f:
        for node, category in csv.reader(f):
            node_categories[node].add(category)

    # Group nodes by their category set
    category_sets = defaultdict(list)
    for node in nodes:
        cat_tuple = tuple(sorted(node_categories.get(node, set())))
        category_sets[cat_tuple].append(node)

    # Assign colors to unique category sets
    unique_sets = list(category_sets.keys())
    num_categories = len(unique_sets)

    # Generate colors for both modes
    if num_categories == 0:
        light_palette = ['#CCCCCC']
        dark_palette = ['#666666']
    else:
        light_palette = get_palette('light', num_categories)
        dark_palette = get_palette('dark', num_categories)

    # Create color mappings for both modes
    light_set_colors = {}
    dark_set_colors = {}
    for i, cat_set in enumerate(unique_sets):
        light_set_colors[cat_set] = light_palette[i % len(light_palette)]
        dark_set_colors[cat_set] = dark_palette[i % len(dark_palette)]

    # Process both modes
    for mode in ['light', 'dark']:
        set_colors = light_set_colors if mode == 'light' else dark_set_colors
        text_color = 'black' if mode == 'light' else 'white'
        border_color = 'black' if mode == 'light' else 'white'
        edge_color = '#000000C0' if mode == 'light' else '#FFFFFFC0'

        # Create graph
        dot = Digraph(comment='Graph', format='png')
        dot.attr(
            rankdir='BT',
            nodesep='0.5',
            ranksep='0.8',
            mclimit='15.0',
            newrank='true',
        )

        dot.attr('edge',
            color=edge_color,
            arrowsize='0.8',
            arrowhead='vee'
        )

        # For dark mode, set a dark background
        if mode == 'dark':
            dot.attr(bgcolor='#1a1a1a')

        # Add nodes with appropriate colors
        for node in nodes:
            cat_set = tuple(sorted(node_categories.get(node, set())))
            color = set_colors[cat_set]

            dot.node(node, node,
                     color=border_color,
                     fillcolor=color,
                     style="filled",
                     fontcolor=text_color,
                     penwidth='1.5')

        # Add edges
        with open(edge_path, 'r') as f:
            for src, dst in csv.reader(f):
                if src in nodes and dst in nodes:
                    dot.edge(src, dst)

        # Add legend
        legend_border = 'lightgrey' if mode == 'dark' else 'grey'
        legend_fontcolor = 'white' if mode == 'dark' else 'black'

        with dot.subgraph(name='cluster_legend_padding') as c0:
            c0.attr(
                style='invisible',
                margin='50'
            )
            with c0.subgraph(name='cluster_legend') as c:
                c.attr(
                    style='filled',
                    color=legend_border,
                    fillcolor='transparent',
                    margin='10'
                )

                # Build legend as HTML table
                sorted_sets = sorted(set_colors.items(), key=lambda x: str(x[0]))

                rows = []
                # Entries with internal padding via CELLPADDING
                for cat_set, color in sorted_sets:
                    if not cat_set:
                        label = 'No category'
                    else:
                        label = ', '.join(cat_set)
                        if len(label) > 30:
                            parts = []
                            current = ''
                            for word in label.split(', '):
                                if len(current) + len(word) > 30:
                                    parts.append(current)
                                    current = word
                                else:
                                    current = current + ', ' + word if current else word
                            if current:
                                parts.append(current)
                            label = '<BR/>'.join(parts)

                    color_cell = f'<TD BGCOLOR="{color}" WIDTH="25" HEIGHT="20" BORDER="1" CELLPADDING="5"> </TD>'
                    label_cell = f'<TD ALIGN="LEFT" CELLPADDING="5"><FONT COLOR="{text_color}">{label}</FONT></TD>'
                    rows.append(f'<TR>{color_cell}{label_cell}</TR>')

                legend_html = f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3" CELLPADDING="10">
                    {''.join(rows)}
                </TABLE>>'''
                c.node('legend_table', label=legend_html, shape='plaintext')

        # Render to the data directory with mode suffix
        output_path = data_dir / f'graph_{mode}'
        dot.render(str(output_path), view=False)
        print(f"Generated {output_path}.png")

def main():
    # Get all subdirectories under 'out'
    out_dir = Path('out')
    if not out_dir.exists():
        print(f"Error: {out_dir} directory not found")
        sys.exit(1)

    # Find all directories that contain the required CSV files
    data_dirs = []
    for root, dirs, files in os.walk(out_dir):
        root_path = Path(root)
        if (root_path / 'node.csv').exists() and \
           (root_path / 'edge.csv').exists() and \
           (root_path / 'category.csv').exists():
            data_dirs.append(root_path)

    if not data_dirs:
        print(f"Warning: No directories found containing node.csv, edge.csv, and category.csv under {out_dir}")
        sys.exit(0)

    # Process each directory
    for data_dir in data_dirs:
        print(f"\nProcessing {data_dir}...")
        process_directory(data_dir)

    print("\nAll graphs generated successfully!")

if __name__ == "__main__":
    main()
