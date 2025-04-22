#!/bin/bash
ollama serve &
sleep 5  # Wait for Ollama to start
python parse_clinical_notes.py
