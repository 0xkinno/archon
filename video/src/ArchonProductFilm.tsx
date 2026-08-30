import React from "react";
import { Sequence, useVideoConfig } from "remotion";
import { Scene1_BrandReveal } from "./scenes/Scene1_BrandReveal";
import { Scene2_TheProblem } from "./scenes/Scene2_TheProblem";
import { Scene3_SystemArchitecture } from "./scenes/Scene3_SystemArchitecture";
import { Scene4_WorkflowExecution } from "./scenes/Scene4_WorkflowExecution";
import { Scene5_GovernanceInAction } from "./scenes/Scene5_GovernanceInAction";
import { Scene6_MemoryAndHeroClose } from "./scenes/Scene6_MemoryAndHeroClose";

export const ArchonProductFilm: React.FC = () => {
  const { fps } = useVideoConfig();
  const timeScale = fps / 30;

  const f1 = Math.round(150 * timeScale); // 5.0s
  const f2 = Math.round(150 * timeScale); // 5.0s
  const f3 = Math.round(150 * timeScale); // 5.0s
  const f4 = Math.round(180 * timeScale); // 6.0s
  const f5 = Math.round(135 * timeScale); // 4.5s
  const f6 = Math.round(135 * timeScale); // 4.5s

  const start1 = 0;
  const start2 = start1 + f1;
  const start3 = start2 + f2;
  const start4 = start3 + f3;
  const start5 = start4 + f4;
  const start6 = start5 + f5;

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: "#050811",
        position: "relative",
        overflow: "hidden",
        width: "100%",
        height: "100%",
      }}
    >
      {/* 0.0s - 5.0s: Scene 1 Brand Reveal */}
      <Sequence from={start1} durationInFrames={f1}>
        <Scene1_BrandReveal />
      </Sequence>

      {/* 5.0s - 10.0s: Scene 2 The Problem */}
      <Sequence from={start2} durationInFrames={f2}>
        <Scene2_TheProblem />
      </Sequence>

      {/* 10.0s - 15.0s: Scene 3 System Architecture */}
      <Sequence from={start3} durationInFrames={f3}>
        <Scene3_SystemArchitecture />
      </Sequence>

      {/* 15.0s - 21.0s: Scene 4 Workflow Execution */}
      <Sequence from={start4} durationInFrames={f4}>
        <Scene4_WorkflowExecution />
      </Sequence>

      {/* 21.0s - 25.5s: Scene 5 Governance In Action */}
      <Sequence from={start5} durationInFrames={f5}>
        <Scene5_GovernanceInAction />
      </Sequence>

      {/* 25.5s - 30.0s: Scene 6 Memory & Hero Close */}
      <Sequence from={start6} durationInFrames={f6}>
        <Scene6_MemoryAndHeroClose />
      </Sequence>
    </div>
  );
};
