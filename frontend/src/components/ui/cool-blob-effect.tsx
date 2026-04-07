import React from "react";
import "./cool-blob.css"; // 👈 we’ll add this CSS next

export function Component() {
  return (
    <div className="blob-container">
      <div className="blob blob-1"></div>
      <div className="blob blob-2"></div>
      <div className="blob blob-3"></div>
    </div>
  );
}

export default Component;
