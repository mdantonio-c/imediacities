import { NgModule } from "@angular/core";
import { AppVideoControlStepComponent } from "./app-video-control-step/app-video-control-step";
import { AppVideoControlAdvancedComponent } from "./app-video-control-advanced/app-video-control-advanced";
import { AppVideoControlFforwardComponent } from "./app-video-control-fforward/app-video-control-fforward";
import { AppVideoControlFpsComponent } from "./app-video-control-fps/app-video-control-fps";
import { AppVideoControlFrewindComponent } from "./app-video-control-frewind/app-video-control-frewind";
import { AppVideoControlFullscreenComponent } from "./app-video-control-fullscreen/app-video-control-fullscreen";
import { AppVideoControlGotoEndComponent } from "./app-video-control-goto-end/app-video-control-goto-end";
import { AppVideoControlGotoStartComponent } from "./app-video-control-goto-start/app-video-control-goto-start";
import { AppVideoControlPlayComponent } from "./app-video-control-play/app-video-control-play";
import { AppVideoControlProgressBarComponent } from "./app-video-control-progress-bar/app-video-control-progress-bar";
import { AppVideoControlSwitchComponent } from "./app-video-control-switch/app-video-control-switch";
import { AppVideoControlTimeMarkersComponent } from "./app-video-control-time-markers/app-video-control-time-markers";
import { AppVideoControlTimerangeComponent } from "./app-video-control-timerange/app-video-control-timerange";
import { AppVideoControlVolumeComponent } from "./app-video-control-volume/app-video-control-volume";
import { AppVideoControlRangeComponent } from "./app-video-control-range/app-video-control-range";
import { AppVideoControlJumpToComponent } from "./app-video-control-jump-to/app-video-control-jump-to";
import { AppVideoControlFieldComponent } from "./app-video-control-field/app-video-control-field";

export const appVideoControlsDeclarations: any[] = [
  AppVideoControlAdvancedComponent,
  AppVideoControlFforwardComponent,
  AppVideoControlFpsComponent,
  AppVideoControlFieldComponent,
  AppVideoControlFrewindComponent,
  AppVideoControlFullscreenComponent,
  AppVideoControlGotoEndComponent,
  AppVideoControlGotoStartComponent,
  AppVideoControlJumpToComponent,
  AppVideoControlPlayComponent,
  AppVideoControlProgressBarComponent,
  AppVideoControlRangeComponent,
  AppVideoControlStepComponent,
  AppVideoControlSwitchComponent,
  AppVideoControlTimeMarkersComponent,
  AppVideoControlTimerangeComponent,
  AppVideoControlVolumeComponent,
];
