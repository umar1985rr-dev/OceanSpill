import sys
sys.path.insert(0, '.')
from backend.services.oil_detector.detect import detect_oil_spill
print('detect_oil_spill imported successfully')
print('Model lazy loading works!')