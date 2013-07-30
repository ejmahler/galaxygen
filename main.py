
import json

import generator, printer

def main():
    stars, edges = generator.generate_galaxy(5000)
    
    '''with open('starData.json', 'w') as datafile:
        json.dump({"stars":stars, "edges":edges}, datafile)'''
    
    printer.print_galaxy(stars, edges, y_index=1)

if(__name__ == '__main__'):
    main()
