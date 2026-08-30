import React from "react";
import { registerRoot, Composition } from "remotion";
import { ArchonProductFilm } from "./ArchonProductFilm";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 30 FPS Master (1920x1080 @ 30fps, 900 frames = 30.0s) */}
      <Composition
        id="ArchonFilm30"
        component={ArchonProductFilm}
        durationInFrames={900}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{}}
      />

      {/* 60 FPS Master (1920x1080 @ 60fps, 1800 frames = 30.0s) */}
      <Composition
        id="ArchonProductFilm"
        component={ArchonProductFilm}
        durationInFrames={1800}
        fps={60}
        width={1920}
        height={1080}
        defaultProps={{}}
      />
    </>
  );
};

registerRoot(RemotionRoot);
