// Makes mouse rotation the same speed in both directions in the CadQuery 3D
// viewer (cadquery.cq_directive) and shows the mouse controls when hovering over a view.
(function () {
  if (typeof interactor === "undefined" || typeof manips === "undefined") {
    return;
  }

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
