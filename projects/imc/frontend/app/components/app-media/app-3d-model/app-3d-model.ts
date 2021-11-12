import {
  Component,
  Input,
  AfterViewInit,
  ViewChild,
  ElementRef,
} from "@angular/core";
import { AuthService } from "@rapydo/services/auth";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

@Component({
  selector: "app-3d-model",
  templateUrl: "app-3d-model.html",
  styleUrls: ["app-3d-model.css"],
})
export class App3dModelComponent implements AfterViewInit {
  @Input() data;

  @Input() public cameraZ: number = 50;
  @Input() public fieldOfView: number = 1;
  @Input("nearClipping") public nearClippingPlane: number = 1;
  @Input("farClipping") public farClippingPlane: number = 1000;

  @ViewChild("canvas") private canvasRef: ElementRef;

  // Instantiate a loader
  private gltfLoader: GLTFLoader = new GLTFLoader();
  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private controls!: OrbitControls;

  constructor(private auth: AuthService) {}

  // @ts-ignore
  private get canvas(): HTMLCanvasElement {
    return this.canvasRef.nativeElement;
  }

  /**
   * Load a glTF resource.
   * @private
   */
  private loadGLTFModel() {
    const path = "/app/custom/assets/models/gltf/porsche/scene.gltf";
    this.gltfLoader.load(
      path,
      (gltf) => {
        this.scene.add(gltf.scene);
        console.log("gltf model added to the scene");
      },
      (xhr) => {
        // Progress Event
        console.log((xhr.loaded / xhr.total) * 100 + "% loaded");
      },
      (error) => {
        console.error("Error", error, error.message);
      }
    );
  }

  /**
   * Create the scene
   * @private
   */
  private createScene() {
    //* Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xacacac);
    this.loadGLTFModel();
    //* Camera
    let aspectRatio = this.getAspectRatio();
    this.camera = new THREE.PerspectiveCamera(
      this.fieldOfView,
      aspectRatio,
      this.nearClippingPlane,
      this.farClippingPlane
    );
    this.camera.position.z = this.cameraZ;
    this.camera.position.set(200, 300, this.cameraZ);

    // setup light
    /*const skyColor = 0xB1E1FF;  // light blue
    const groundColor = 0xB97A20;  // brownish orange
    const intensity = 1;
    const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
    this.scene.add(light);*/

    const color = 0xffffff;
    const intensity = 3;
    const light = new THREE.DirectionalLight(color, intensity);
    light.position.set(1, 5, 2);
    this.scene.add(light);
    this.scene.add(light.target);

    // controls
    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.target.set(0, 0, 0);
    this.controls.update();
  }

  private getAspectRatio() {
    return this.canvas.clientWidth / this.canvas.clientHeight;
  }

  /**
   * Start the rendering loop
   * @private
   * @memberof App3dModelComponent
   */
  private render() {
    console.log("render");
    //* Renderer
    // Use canvas element in template
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas });
    this.renderer.setPixelRatio(devicePixelRatio);
    this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);

    let component: App3dModelComponent = this;
    (function render() {
      requestAnimationFrame(render);
      component.renderer.render(component.scene, component.camera);
    })();
  }

  ngAfterViewInit() {
    this.createScene();
    this.render();
  }
}
