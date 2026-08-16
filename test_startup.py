import sys
sys.path.insert(0, '.')
from backend.services.oil_detector.detect import detect_oil_spill
print('SUCCESS: detect_oil_spill imported without loading model at import time')
print('Lazy loading works!')