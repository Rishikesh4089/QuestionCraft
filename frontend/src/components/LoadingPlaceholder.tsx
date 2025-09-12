import React from "react";
import Spinner from "./Spinner";

const LoadingPlaceholder: React.FC = () => (
  <div className="text-center text-slate-500">
    <Spinner size="large" />
    <h3 className="mt-4 text-lg font-medium">Generating your paper...</h3>
    <p className="mt-1 text-sm">Analyzing documents and crafting questions.</p>
  </div>
);

export default LoadingPlaceholder;
