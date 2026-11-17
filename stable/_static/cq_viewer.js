// Fixes mouse rotation in the CadQuery 3D viewer (cadquery.cq_directive) and
// shows the mouse controls when hovering over a view.
(function () {
  if (typeof interactor === "undefined" || typeof manips === "undefined") {
    return;
  }

  // TODO remove this part once a CadQuery release includes
  // https://github.com/CadQuery/cadquery/pull/2124
  // The viewer binds the interactor to document.body and vtk.js scales mouse
  // positions by the size of the bound element, so on long pages vertical drags
  // were shrunk and up and down rotation was very slow. This listens on the body
  // but reports the canvas size.
  const eventContainer = {
    addEventListener: (...args) => document.body.addEventListener(...args),
    removeEventListener: (...args) => document.body.removeEventListener(...args),
    getBoundingClientRect: () => openglRenderWindow.getCanvas().getBoundingClientRect(),
  };
  // render() looks this function up by name, so the views use this version
  enterCurrentRenderer = function (e) {
    interactor.bindEvents(eventContainer);
    interact_style.setEnabled(true);
    interactor.setCurrentRenderer(RENDERERS[e.target.id]);
  };

  // The vtk.js rotate manipulator turns a drag across the full window width or
  // height into a full turn, so on a wide window up and down rotated faster than
  // left and right. This replaces it with one that rotates by the same angle per
  // pixel in both directions. vtk.js objects are frozen, so it is built with
  // extend to allow the mouse move handler to be wrapped.
  const rotate = {};
  vtk.Interaction.Manipulators.vtkMouseCameraTrackballRotateManipulator.extend(rotate, {});
  rotate.setUseFocalPointAsCenterOfRotation(true);
  const buttonDown = rotate.onButtonDown;
  const mouseMove = rotate.onMouseMove;
  let lastY = 0;
  let scaledY = 0;
  rotate.onButtonDown = function (interactor, renderer, position) {
    lastY = scaledY = position.y;
    return buttonDown(interactor, renderer, position);
  };
  rotate.onMouseMove = function (interactor, renderer, position) {
    if (position) {
      const [width, height] = interactor.getView().getSize();
      scaledY += ((position.y - lastY) * height) / width;
      lastY = position.y;
      position = Object.assign({}, position, { y: scaledY });
    }
    return mouseMove(interactor, renderer, position);
  };
  interact_style.removeMouseManipulator(manips.rot);
  interact_style.addMouseManipulator(rotate);
  manips.rot = rotate;

  // shows the mouse controls when hovering over a view
  const controls = [
    "Rotate: left drag",
    "Zoom: right drag or Ctrl + left drag",
    "Pan: middle drag",
    "Roll: Shift + left drag",
  ].join("\n");
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".cq-vtk").forEach((view) => {
      view.title = controls;
    });
  });
})();
