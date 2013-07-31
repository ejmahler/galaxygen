
import argparse
import json


import serialize

def main(options):
    import generator, printer
    
    stars, edges = generator.generate_galaxy(
        num_stars=5000, 
        galaxy_radius=2000, 
        
        spiral_arm_count=6, 
        spiral_tightness=0.4, 
        
        disk_height=50, 
        bulge_height=150
        )
    
        
    serialize.save(stars, edges, options.filename)
    
    printer.print_galaxy(stars, edges, y_index=1, image_size=2400)
    
    
    
def run_layout(options):
    import layout
    
    star_array, edge_data = serialize.load(options.filename)
    
    layout.forced_directed_layout(star_array, edge_data, iterations=options.iterations)
    
    serialize.save(star_array, edge_data, options.filename)
    
    
    

def run_render(options):
    import printer
    
    star_array, edge_data = serialize.load(options.filename)
    
    if(options.edge):
        y_index=2
    else:
        y_index=1
    
    printer.print_galaxy(star_array, edge_data, y_index=y_index)
    
    
    

if(__name__ == '__main__'):
    parser = argparse.ArgumentParser('Functions for randomly generating a galaxy similar to the one in EVE Online')
    parser.add_argument('-f','--filename', help="File name to load and save star data to and from", type=str, default=serialize.default_json_filename)
    
    subparsers = parser.add_subparsers(title="Subcommands")
    
    layout_parser = subparsers.add_parser('main', help='Generates a new galaxy, renders it, and serializes it')
    layout_parser.set_defaults(func=main)
    
    layout_parser = subparsers.add_parser('layout', help='Takes an existing star data set and runs iterations of force layout on them. Can be run on pypy, unlike the rest of the galaxy generator modules')
    layout_parser.add_argument('-i','--iterations', help="Number of iterations to run", type=int, default=1)
    layout_parser.set_defaults(func=run_layout)
    
    render_parser = subparsers.add_parser('render', help='Takes an existing star data set and generates an image for it')
    render_parser.add_argument('-e','--edge', help="Print the galaxy edge-on instead of top-down", action='store_true')
    render_parser.set_defaults(func=run_render)
    
    args = parser.parse_args()
    args.func(args)
