import { lazy, Suspense } from "react";
import { Route, Switch } from "wouter";
import { Layout } from "@/components/Layout";
import Landing from "@/pages/Landing";

const Analyze = lazy(() => import("@/pages/Analyze"));
const Performance = lazy(() => import("@/pages/Performance"));
const Knowledge = lazy(() => import("@/pages/Knowledge"));
const ModelCard = lazy(() => import("@/pages/ModelCard"));
const About = lazy(() => import("@/pages/About"));
const Settings = lazy(() => import("@/pages/Settings"));
const History = lazy(() => import("@/pages/History"));
const Ask = lazy(() => import("@/pages/Ask"));
const CaseGallery = lazy(() => import("@/pages/CaseGallery"));
const ClinicalEvidence = lazy(() => import("@/pages/ClinicalEvidence"));
const ReportPreview = lazy(() => import("@/pages/ReportPreview"));
const ResearchReport = lazy(() => import("@/pages/ResearchReport"));
const DemoMode = lazy(() => import("@/pages/DemoMode"));
const Deployment = lazy(() => import("@/pages/Deployment"));
const DatasetRegistry = lazy(() => import("@/pages/DatasetRegistry"));
const Login = lazy(() => import("@/pages/Login"));

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
      <Suspense fallback={<div className="mx-auto max-w-6xl px-6 py-20" role="status"><div className="h-3 w-32 animate-pulse rounded bg-line" /><div className="mt-4 h-10 max-w-xl animate-pulse rounded bg-line" /><div className="mt-6 h-48 animate-pulse rounded-lg border border-line bg-surface" /></div>}>
        <Switch>
        <Route path="/" component={Landing} />
        <Route path="/analyze" component={Analyze} />
        <Route path="/gallery" component={CaseGallery} />
        <Route path="/clinical-evidence" component={ClinicalEvidence} />
        <Route path="/koil" component={ClinicalEvidence} />
        <Route path="/hpv" component={ClinicalEvidence} />
        <Route path="/datasets" component={DatasetRegistry} />
        <Route path="/workflow" component={ClinicalEvidence} />
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
        <Route path="/login" component={Login} />
        <Route component={NotFound} />
        </Switch>
      </Suspense>
    </Layout>
  );
}
