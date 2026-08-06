import PageHeader from "../components/ui/PageHeader";
import SystemCheck from "./SystemCheck";

function SystemPage() {
  return (
    <div>
      <PageHeader
        title="System Health"
        description="Status of all backend services powering OceanSpill"
      />
      <SystemCheck />
    </div>
  );
}

export default SystemPage;
