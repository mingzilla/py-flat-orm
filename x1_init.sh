#!/bin/bash

hatch env remove
hatch env create
hatch shell py-flat-orm
echo $PYTHONPATH