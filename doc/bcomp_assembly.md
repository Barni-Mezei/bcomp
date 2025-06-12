# Bcomp assembly - syntax

## Quick guide (asm V2.0)
- Instructions: `mva 0`
- Comments: `add ; Cool code`
- Labels: `:loop` `jmp :loop`
- Constants: `$magic_number 13` `mvb $magic_number`
- Macros: `#loadStr "Hello, world!" 0`

## Versions

The *bcomp assembly* has many versions, for many architectures, and platforms.

- `1.0`: Architecture: 1.0, Platform: Scrap Mechanic computer
- `1.1`: Architecture: 1.0, Platform: Scrap Mechanic computer 1.1, bcomp_vm_asm1.1
- `2.0`: Architecture: 2.0, Platform: bcomp_vm_asm2.0, Arduino UNO
- `2.1`: Architecture: 2.0, Platform: bcomp_vm_asm2.1, Texas Instruments TI-84 Plus Python edition
- `2.2`: Architecture: 2.1, Platform: bcomp_vm_asm2.2


## Reference

The language syntax changed a lot in asm V2.2, so there are 2 documents.

- `1.1 - 2.1`: [Bcomp assembly](bcomp_assembly_2.0.md)
- `2.2`: [Bcomp assembly](bcomp_assembly_2.2.md)