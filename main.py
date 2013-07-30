
import json

import generator, printer

def main():
    stars, edges = generator.generate_galaxy(num_stars=5000, galaxy_radius=2000, spiral_arm_count=6, spiral_tightness=0.4)
    
    '''with open('starData.json', 'w') as datafile:
        json.dump({"stars":stars, "edges":edges}, datafile)'''
    
    printer.print_galaxy(stars, edges, y_index=1, image_size=2400)

if(__name__ == '__main__'):
    main()
