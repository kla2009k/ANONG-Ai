import { Route, Switch } from "wouter";
import { Layout } from "@/components/Layout";
import Landing from "@/pages/Landing";
import Analyze from "@/pages/Analyze";
import Performance from "@/pages/Performance";
import Knowledge from "@/pages/Knowledge";
import ModelCard from "@/pages/ModelCard";
import About from "@/pages/About";
import Settings from "@/pages/Settings";
import History from "@/pages/History";
import Ask from "@/pages/Ask";
import CaseGallery from "@/pages/CaseGallery";
import Workflow from "@/pages/Workflow";
import ReportPreview from "@/pages/ReportPreview";
import ResearchReport from "@/pages/ResearchReport";
import DemoMode from "@/pages/DemoMode";
import Deployment from "@/pages/Deployment";
import KoilEvidence from "@/pages/KoilEvidence";
import HpvContext from "@/pages/HpvContext";

function NotFound() {
  return (
    <div className="mx-auto max-w-md px-4 py-28 text-center">
      <h1 className="font-display text-6xl font-bold text-teal">404</h1>
      <p className="mt-3 text-mut">The requested page could not be found.</p>
    </div>
  );
}

export default function App() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Landing} />
        <Route path="/analyze" component={Analyze} />
        <Route path="/gallery" component={CaseGallery} />
        <Route path="/koil" component={KoilEvidence} />
        <Route path="/hpv" component={HpvContext} />
        <Route path="/workflow" component={Workflow} />
        <Route path="/reports" component={ReportPreview} />
        <Route path="/research-report" component={ResearchReport} />
        <Route path="/demo" component={DemoMode} />
        <Route path="/deployment" component={Deployment} />
        <Route path="/performance" component={Performance} />
        <Route path="/knowledge" component={Knowledge} />
        <Route path="/history" component={History} />
        <Route path="/ask" component={Ask} />
        <Route path="/model" component={ModelCard} />
        <Route path="/about" component={About} />
        <Route path="/settings" component={Settings} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}
