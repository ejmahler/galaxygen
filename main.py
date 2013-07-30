
import json

import generator, printer, layout, serialize

def main():
    stars, edges = generator.generate_galaxy(
        num_stars=5000, 
        galaxy_radius=2000, 
        
        spiral_arm_count=6, 
        spiral_tightness=0.4, 
        
        disk_height=50, 
        bulge_height=150
        )
    
        
    serialize.save(stars, edges)
        
    #layout.forced_directed_layout(stars, edges, iterations=1)
    
    printer.print_galaxy(stars, edges, y_index=1, image_size=2400)

if(__name__ == '__main__'):
    main()
