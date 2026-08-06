import PageHeader from "../components/ui/PageHeader";
import OilSpillDetector from "../components/OilSpillDetector";

function ImageDetection() {
  return (
    <div>
      <PageHeader
        title="Satellite Image Detection"
        description="Upload a satellite image for AI-based oil spill segmentation (U-Net model)"
      />
      <OilSpillDetector />
    </div>
  );
}

export default ImageDetection;
