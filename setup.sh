#!/bin/bash

echo "Installing package dependencies with pip..."
for module in inky inkyphat pillow buttonshim numpy geocoder requests bs4; do
	echo "Installing $module..."
	pip install $module;
	done


