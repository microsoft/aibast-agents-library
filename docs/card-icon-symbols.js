import * as T from "../vendor/three/three.module.min.js";

export function cardSymbols(material) {
  const mesh = (geometry, position = [0, 0, 0], rotation = [0, 0, 0]) => {
    const object = new T.Mesh(geometry, material);
    object.position.set(...position);
    object.rotation.set(...rotation);
    return object;
  };
  const group = (...children) => new T.Group().add(...children);
  const box = (w, h, d) => new T.BoxGeometry(w, h, d);
  const extrude = (points, depth = 0.3, holes = []) => {
    const vectors = list => list.map(([x, y]) => new T.Vector2(x, y));
    const shape = new T.Shape(vectors(points));
    holes.forEach(hole => shape.holes.push(new T.Path(vectors(hole))));
    const geometry = new T.ExtrudeGeometry(shape, {
      depth, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.03,
      bevelSegments: 2, curveSegments: 32
    });
    geometry.center();
    return geometry;
  };
  const circle = radius => Array.from({length: 40}, (_, i) => {
    const angle = -i / 40 * Math.PI * 2;
    return [Math.cos(angle) * radius, Math.sin(angle) * radius];
  });
  const gear = Array.from({length: 32}, (_, i) => {
    const angle = (i - 0.5) / 32 * Math.PI * 2;
    const radius = i % 4 < 2 ? 1 : 0.74;
    return [Math.cos(angle) * radius, Math.sin(angle) * radius];
  });
  const star = Array.from({length: 8}, (_, i) => {
    const angle = i / 8 * Math.PI * 2 + Math.PI / 2;
    const radius = i % 2 ? 0.3 : 1;
    return [Math.cos(angle) * radius, Math.sin(angle) * radius];
  });
  const symbols = {
    b2b_sales: group(mesh(extrude([
      [-0.75, -0.14], [0.2, -0.14], [0.2, -0.5], [0.95, 0],
      [0.2, 0.5], [0.2, 0.14], [-0.75, 0.14]
    ]), [0, 0, 0], [0, 0, Math.PI / 4])),
    b2c_sales: group(
      mesh(new T.TorusGeometry(0.8, 0.13, 16, 48)),
      mesh(new T.SphereGeometry(0.25, 24, 16))
    ),
    energy: group(mesh(extrude([
      [0.12, 1], [-0.55, -0.08], [-0.08, -0.08], [-0.22, -1],
      [0.55, 0.18], [0.06, 0.18]
    ]))),
    financial_services: group(mesh(new T.OctahedronGeometry(0.95))),
    general: group(mesh(extrude(star))),
    healthcare: group(mesh(extrude([
      [-0.28, 0.9], [0.28, 0.9], [0.28, 0.28], [0.9, 0.28],
      [0.9, -0.28], [0.28, -0.28], [0.28, -0.9], [-0.28, -0.9],
      [-0.28, -0.28], [-0.9, -0.28], [-0.9, 0.28], [-0.28, 0.28]
    ]))),
    human_resources: group(mesh(extrude(
      [[0, 1], [0.9, 0], [0, -1], [-0.9, 0]], 0.3,
      [[[0, 0.55], [-0.5, 0], [0, -0.55], [0.5, 0]]]
    ))),
    manufacturing: group(mesh(extrude(gear, 0.3, [circle(0.34)]))),
    professional_services: group(
      mesh(box(1.5, 1, 0.5), [0, -0.15, 0]),
      mesh(new T.TorusGeometry(0.3, 0.07, 12, 32, Math.PI), [0, 0.35, 0])
    ),
    retail_cpg: group(...[-1, 1].flatMap(x => [-1, 1].map(y =>
      mesh(box(0.62, 0.62, 0.62), [x * 0.4, y * 0.4, 0])
    ))),
    slg_government: group(mesh(extrude([
      [-0.85, 0.1], [0, 0.95], [0.85, 0.1], [0.6, 0.1],
      [0.6, -0.85], [0.18, -0.85], [0.18, -0.3], [-0.18, -0.3],
      [-0.18, -0.85], [-0.6, -0.85], [-0.6, 0.1]
    ]))),
    software_digital_products: group(...[0, 1, 2].map(i =>
      mesh(box(1.35, 0.14, 1.35), [0, -0.42 + i * 0.42, 0], [0, Math.PI / 4, 0])
    )),
    telecom_media_gaming: group(mesh(extrude([[-0.6, -0.85], [0.85, 0], [-0.6, 0.85]], 0.22))),
    customer_service: group(mesh(extrude([
      [-0.9, 0.75], [0.9, 0.75], [0.9, -0.3], [-0.1, -0.3],
      [-0.55, -0.85], [-0.5, -0.3], [-0.9, -0.3]
    ])))
  };
  for (const [kind, symbol] of Object.entries(symbols)) {
    const front = kind === "telecom_media_gaming" || kind === "b2c_sales";
    symbol.rotation.set(front ? 0.08 : 0.25, front ? -0.16 : -0.55, 0);
    symbol.userData.rest = symbol.rotation.clone();
    const size = new T.Box3().setFromObject(symbol).getSize(new T.Vector3());
    symbol.scale.setScalar(1.9 / Math.max(size.x, size.y));
    symbol.visible = false;
  }
  return symbols;
}
