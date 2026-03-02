######################################
# Author : Snow Yang
# Date   : 2018-12-03
# Mail   : yangsw@mxchip.com
######################################

set MFLASH_ENTRY_LOC     $($MFLASH_CONFIG_START + 0x00)
set MFLASH_BUF_SIZE_LOC  $($MFLASH_CONFIG_START + 0x04)
set MFLASH_RDY_LOC       $($MFLASH_CONFIG_START + 0x08)
set MFLASH_CMD_LOC       $($MFLASH_CONFIG_START + 0x0C)
set MFLASH_RET_LOC       $($MFLASH_CONFIG_START + 0x10)
set MFLASH_ARG0_LOC      $($MFLASH_CONFIG_START + 0x14)
set MFLASH_ARG1_LOC      $($MFLASH_CONFIG_START + 0x18)
set MFLASH_BUF_LOC       $($MFLASH_CONFIG_START + 0x1C)

proc memread32 {address} {

    # mem2array memar 32 $address 1
    # return $memar(0)
    set value [read_memory $address 32 1]
    return [lindex $value 0]
}

proc load_image_at_offset {fname foffset target_addr length} {
    # Jim Tcl: file tempfile returns filename (not channel like Tcl 8.6)
    set tmp_file [file tempfile]

    exec dd if=$fname of=$tmp_file bs=1 skip=$foffset count=$length
    load_image $tmp_file $target_addr bin
    file delete $tmp_file
}

proc load_image_bin {fname foffset address length } {
    # load_image $fname [expr $address - $foffset] bin $address $length
    load_image_at_offset $fname $foffset $address $length
}

proc mflash_init { mloader } {

    global mflash_buf_size

    load_image $mloader

    set mflash_entry [memread32 $::MFLASH_ENTRY_LOC]
    set mflash_buf_size [memread32 $::MFLASH_BUF_SIZE_LOC]
	
    reg pc $mflash_entry

    if { $::MFLASH_RUN_WITH_HALT == 0 } {
        resume
    }
}

proc mflash_cmd_run { timeout } {

    mww $::MFLASH_RDY_LOC 1

    loop t 0 $timeout 1 {
        if { $::MFLASH_RUN_WITH_HALT == 1 } {
            resume
        }
        #after 3
        after 2
        if { $::MFLASH_RUN_WITH_HALT == 1 } {
            halt
        }
        set ret [memread32 $::MFLASH_RDY_LOC]  
        if { $ret == 0 } {
            set ret [memread32 $::MFLASH_RET_LOC]
            return $ret
        }
    }
    
    error "error"
    exit -1;
}
