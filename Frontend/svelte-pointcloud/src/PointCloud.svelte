<script>
    import { onMount } from 'svelte';
    import * as THREE from 'three';
    import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
    import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
  
    let container;
  
    onMount(() => {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        // Custom keyboard controls
        const speed = 0.1;
        window.addEventListener('keydown', (event) => {
        switch (event.key) {
            case 'ArrowUp':
            // Move forward
            camera.position.add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(speed));
            break;
            case 'ArrowDown':
            // Move backward
            camera.position.add(camera.getWorldDirection(new THREE.Vector3()).multiplyScalar(-speed));
            break;
            case 'ArrowLeft':
            // Move left
            camera.position.x -= speed;
            break;
            case 'ArrowRight':
            // Move right
            camera.position.x += speed;
            break;
        }
        });

    camera.position.z = 5;
  
      const loadPointCloud = async () => {
        const loader = new PLYLoader();
        // const data = await fetch('YOUR_API_ENDPOINT_HERE').then(res => res.arrayBuffer());
        loader.load("pointcloud.ply", function (geometry) {
          geometry.computeVertexNormals();
          // Adjustments for Three.js r126 and later
            if (geometry.attributes.color) {
                geometry.attributes.color.normalized = true; // Ensure normalized color values
            }
            const material = new THREE.PointsMaterial({
                size: 0.05,
                vertexColors: true // Correct way to enable vertex colors
            });
          const pointCloud = new THREE.Points(geometry, material);
          scene.add(pointCloud);
        });
      };
  
      loadPointCloud();
  
      const animate = function () {
        requestAnimationFrame(animate);
        controls.update(); // Only required if controls.enableDamping = true, or if controls.autoRotate = true
        renderer.render(scene, camera);
      };
  
      animate();
  
      return () => {
        container.removeChild(renderer.domElement);
      };
    });
  </script>
  
  <div bind:this={container}></div>
  
  <style>
    div {
      width: 100%;
      height: 100vh;
    }
  </style>
  