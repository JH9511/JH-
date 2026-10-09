#![cfg(feature = "corpus")]

use photocraft_io::{ExportOptions, export, import};
use std::path::Path;

#[test]
#[ignore = "requires psd-tools; see docs/development.md"]
fn export_for_independent_reader() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let output = std::env::var_os("PHOTOCRAFT_PSD_EXPORTS").expect("set PHOTOCRAFT_PSD_EXPORTS");
    for name in [
        "psd-tools/1layer.psd",
        "psd-tools/1layer.psb",
        "psd-tools/16bit5x5.psd",
        "psd-tools/16bit5x5.psb",
        "psd-tools/32bit5x5.psd",
        "psd-tools/32bit5x5.psb",
        "psd-tools/gray0.psd",
        "psd-tools/colormodes/4x4_8bit_cmyk.psd",
        "psd-tools/mask-index.psd",
        "psd-tools/empty-group.psd",
        "psd-tools/colorprofiles/north_america_newspaper.psd",
        "psd/ag-psd/read-write/group-blend/src.psd",
    ] {
        let bytes = std::fs::read(root.join("corpus").join(name)).expect(name);
        let document = import(name, &bytes).expect(name).document;
        let result = export(&document, name, &ExportOptions::default()).expect(name);
        let path = Path::new(&output).join(name);
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, result.bytes).expect(name);
    }
}
