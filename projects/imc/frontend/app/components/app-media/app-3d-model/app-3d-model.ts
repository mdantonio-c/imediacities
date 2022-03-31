import {
  Component,
  Input,
  OnInit,
  AfterViewInit,
  ViewChild,
  ElementRef,
  HostListener,
} from "@angular/core";
import { AuthService } from "@rapydo/services/auth";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

@Component({
  selector: "app-3d-model",
  templateUrl: "app-3d-model.html",
  styleUrls: ["app-3d-model.scss"],
})
export class App3dModelComponent implements OnInit, AfterViewInit {
  @Input() data;

  @Input() public cameraZ: number = -100;
  @Input() public fieldOfView: number = 20;
  @Input("nearClipping") public nearClippingPlane: number = 1;
  @Input("farClipping") public farClippingPlane: number = 1000;

  @ViewChild("canvas") private canvasRef: ElementRef;

  // Instantiate a loader
  private gltfLoader: GLTFLoader = new GLTFLoader();
  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  public camera!: THREE.PerspectiveCamera;
  private controls!: OrbitControls;
  // Helpers
  private axesHelper = new THREE.AxesHelper(5);
  private dirLightHelper: THREE.DirectionalLightHelper;

  private isFullScreen: boolean;
  public showHelp: boolean = false;
  public showHelpers: boolean = false;

  constructor(private auth: AuthService) {}

  ngOnInit() {
    this.checkScreenMode();
  }

  // @ts-ignore
  private get canvas(): HTMLCanvasElement {
    return this.canvasRef.nativeElement;
  }

  /**
   * Load a glTF/glb resource.
   * @private
   */
  private loadGLTFModel() {
    // const path = "/app/custom/assets/models/gltf/bassorilievo/bassorilievo.glb";
    const path = this.data.links.content;
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
    // this.camera.position.set(1.4, 1, this.cameraZ);

    // setup light
    const color = 0xffffff;
    const intensity = 0.8;
    /*const skyColor = 0xB1E1FF;  // light blue
    const groundColor = 0xB97A20;  // brownish orange
    */

    /*const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
    this.scene.add(light);*/

    const dirLight = new THREE.DirectionalLight(color, intensity);
    dirLight.position.set(2, 2, -5); // x, y, z
    this.scene.add(dirLight);
    // this.scene.add(light.target);

    const ambientLight = new THREE.AmbientLight(color, intensity);
    ambientLight.position.set(0, 0, 10);
    this.scene.add(ambientLight);

    // controls
    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.target.set(0, 0.4, 0);
    this.controls.update();

    // add helpers
    this.dirLightHelper = new THREE.DirectionalLightHelper(dirLight, 5);
    if (this.showHelpers) {
      this.scene.add(this.axesHelper);
      this.scene.add(this.dirLightHelper);
    }
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

  @HostListener("document:fullscreenchange", ["$event"])
  @HostListener("document:webkitfullscreenchange", ["$event"])
  @HostListener("document:mozfullscreenchange", ["$event"])
  @HostListener("document:MSFullscreenChange", ["$event"])
  fullscreenModes(event) {
    this.checkScreenMode();
  }

  checkScreenMode(): void {
    if (document.fullscreenElement) {
      // fullscreen
      this.isFullScreen = true;
    } else {
      // not in full screen
      this.isFullScreen = false;
    }
  }

  /**
   * Open fullscreen
   */
  openFullscreen() {
    if (this.canvasRef.nativeElement.requestFullscreen) {
      this.canvasRef.nativeElement.requestFullscreen();
    } else if (this.canvasRef.nativeElement.mozRequestFullScreen) {
      /* Firefox */
      this.canvasRef.nativeElement.mozRequestFullScreen();
    } else if (this.canvasRef.nativeElement.webkitRequestFullscreen) {
      /* Chrome, Safari and Opera */
      this.canvasRef.nativeElement.webkitRequestFullscreen();
    } else if (this.canvasRef.nativeElement.msRequestFullscreen) {
      /* IE/Edge */
      this.canvasRef.nativeElement.msRequestFullscreen();
    }
  }

  /**
   *  Close fullscreen
   */
  closeFullscreen() {
    if (this.canvasRef.nativeElement.exitFullscreen) {
      this.canvasRef.nativeElement.exitFullscreen();
    } else if (this.canvasRef.nativeElement.mozCancelFullScreen) {
      /* Firefox */
      this.canvasRef.nativeElement.mozCancelFullScreen();
    } else if (this.canvasRef.nativeElement.webkitExitFullscreen) {
      /* Chrome, Safari and Opera */
      this.canvasRef.nativeElement.webkitExitFullscreen();
    } else if (this.canvasRef.nativeElement.msExitFullscreen) {
      /* IE/Edge */
      this.canvasRef.nativeElement.msExitFullscreen();
    }
  }

  help(event, op?: string) {
    event.preventDefault();
    switch (op) {
      case "close":
        this.showHelp = false;
        break;
      default:
        this.showHelp = true;
    }
  }

  toggleHelpers() {
    this.showHelpers = !this.showHelpers;
    this.showHelpers
      ? (this.scene.add(this.axesHelper), this.scene.add(this.dirLightHelper))
      : (this.scene.remove(this.axesHelper),
        this.scene.remove(this.dirLightHelper));
  }
}
