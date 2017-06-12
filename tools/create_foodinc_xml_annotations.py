"""Convert a dataset with TXT annotations to XML annotations, respecting
the Pascal VOC format.

Usage:
```shell
python create_foodinc_xml_annotations.py \
    ~/datasets/Foodinc \
    --output_dir Annotations_XML
```
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from PIL import Image

import tensorflow as tf


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description= 
                        'Convert a dataset with TXT annotations to XML ' + 
                        'annotations, respecting the Pascal VOC format.')

    parser.add_argument('dataset',
                        help='The path to the dataset to convert.')
    parser.add_argument('--output_dir', dest='output',
                        default='Annotations_XML',
                        help='The directory where to save the annotations.',
                        type=str)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # Get the arguments
    args = parse_args()

    # Check the dataset
    assert os.path.exists(args.dataset), \
        'Can\'t find the dataset ' + args.dataset
    assert os.path.exists(os.path.join(args.dataset, 'Images')), \
        'Can\'t find the images of the dataset ' + args.dataset
    assert os.path.exists(os.path.join(args.dataset, 'Annotations')), \
        'Can\'t find the annotations of the dataset ' + args.dataset
    assert os.path.isfile(os.path.join(args.dataset, 'infos', 'categories.txt')), \
        'Can\'t find the annotations of the dataset ' + args.dataset

    # Warning if the output annotations directory already exists
    if not os.path.exists(os.path.join(args.dataset, args.output)):
        os.makedirs (os.path.join(args.dataset, args.output))
    else:
        answer = raw_input("The directory " + args.output + " already exists. " +
                           "Do you want to pursue (may affects the existing content)? [y/N] ")
        if not answer.lower() in ("y", "yes"):
            raise SystemExit

    # Main paths
    images_path = os.path.join(args.dataset, 'Images')
    annotations_path = os.path.join(args.dataset, 'Annotations')
    categories_path = os.path.join(args.dataset, 'infos', 'categories.txt')
    annotations_list = os.listdir(annotations_path)
    categories_list = [l.rstrip('\n') for l in open(categories_path)]

    # For each annotations
    for annotations in annotations_list:

        # Image details
        size = Image.open(os.path.join(images_path, annotations[:-4] + ".png")).size

        # Annotations details
        curr_path = os.path.join(annotations_path, annotations)
        split_annot = [l.rstrip('\n').split() for l in open(curr_path)]

        # Create the XML
        annot_xml = ET.Element("annotation")
        ET.SubElement(annot_xml, "folder").text = os.path.basename(args.dataset)
        ET.SubElement(annot_xml, "filename").text = annotations[:-4] + ".png"

        source_xml = ET.SubElement(annot_xml, "source")
        ET.SubElement(source_xml, "database").text = "Foodinc"

        owner_xml = ET.SubElement(annot_xml, "owner")
        ET.SubElement(owner_xml, "company").text = "FiNC"

        size_xml = ET.SubElement(annot_xml, "size")
        ET.SubElement(size_xml, "width").text = str(size[0])
        ET.SubElement(size_xml, "height").text = str(size[1])
        ET.SubElement(size_xml, "depth").text = "3"


        # For each object
        for annot in split_annot:
            obj_xml = ET.SubElement(annot_xml, "object")
            ET.SubElement(obj_xml, "name").text = categories_list[int(annot[0])-1]

            bndbox_xml = ET.SubElement(obj_xml, "bndbox")
            ET.SubElement(bndbox_xml, "xmin").text = annot[1]
            ET.SubElement(bndbox_xml, "ymin").text = annot[2]
            ET.SubElement(bndbox_xml, "xmax").text = annot[3]
            ET.SubElement(bndbox_xml, "ymax").text = annot[4]

        # Write the new annotation
        tree = ET.ElementTree(annot_xml)
        tree.write(os.path.join(args.dataset, args.output, annotations[:-4] + ".xml"))




