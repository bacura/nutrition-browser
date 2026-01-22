//guild.js ver 0.5.3 (2026/01/13)

kp = 'koyomi/'

/////////////////////////////////////////////////////////////////////////////////
// Koyomi //////////////////////////////////////////////////////////////

// Koyomi
const initKoyomi = function(){
	$.post( kp + "koyomi.cgi", { command:"menu" }, function( data ){ $( "#LINE" ).html( data );});
	$.post( kp + "koyomi.cgi", { command:"init" }, function( data ){ $( "#L1" ).html( data ); });

	flashBW();
	dl1 = true;
	dline = true;
	displayBW();
};

// Koyomi
const reKoyomi = function( yyyy, mm ){
	$.post( kp + "koyomi.cgi", { command:"init", yyyy:yyyy, mm:mm }, function( data ){ $( "#L1" ).html( data ); });

	flashBW();
	dl1 = true;
	displayBW();
};

// Set time to now
const nowKoyomi = function( id ){
	var today = new Date();
	var hh = today.getHours();
	var mm = today.getMinutes();
	if( hh < 10 ){ hh = '0' + hh; }
	if( mm < 10 ){ mm = '0' + mm; }
	document.getElementById( id ).value = hh + ':' + mm;
};

/////////////////////////////////////////////////////////////////////////////////
// Koyomi Edit//////////////////////////////////////////////////////////////

// Koyomi edit
const initKoyomiEdit = function( yyyy, mm, dd ){
	$.post( kp + "koyomi-edit.cgi", { command:'init', yyyy:yyyy, mm:mm, dd:dd }, function( data ){
		$( "#L2" ).html( data );
		flashBW();
		dl2 = true;
		dline = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Koyomi fix //////////////////////////////////////////////////////////////

// Initial
const initKoyomiFix = function( yyyy, mm, dd, tdiv ){
	$.post( kp + "koyomi-fix.cgi", { command:'init', yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv }, function( data ){
		$( "#L3" ).html( data );

		dl2 = false;
		dl3 = true;
		displayBW();
	});
};


// Modify or Copy
var modifyKoyomiFix = function( code, yyyy, mm, dd, tdiv, hh_mm, meal_time, order ){
	$.post( kp + "koyomi-fix.cgi", { command:"modify", code:code, yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv, hh_mm:hh_mm, meal_time, order:order }, function( data ){
		$( "#L3" ).html( data );

		dl2 = false;
		dl3 = true;
		displayBW();
	});
};

/////////////////////////////////////////////////////////////////////////////////
// Koyomi import panel//////////////////////////////////////////////////////////////

// Koyomi insert panel
const addKoyomi = function( code ){
	pushBW();
	flashBW();
	$.post( kp + "koyomi-add.cgi", { command:"init", code:code }, function( data ){
		$( "#LF" ).html( data );
		$( '#modal_tip' ).modal( 'hide' );

		dlf = true;
		displayBW();
	});
	$.post( kp + "koyomi.cgi", { command:"menu" }, function( data ){
		$( "#LINE" ).html( data );

		dline = true;
		displayBW();
	});

};

// Koyomi insert panel change
const changeKoyomiAdd = function( com, code, origin ){
	const yyyy_mm_dd = document.getElementById( "yyyy_mm_dd" ).value;
	const tdiv = document.getElementById( "tdiv" ).value;
	const hh_mm = document.getElementById( "hh_mm" ).value;
	const meal_time = document.getElementById( "meal_time" ).value;
	const ev = document.getElementById( "ev" ).value;
	const eu = document.getElementById( "eu" ).value;
	let carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
	$.post( kp + "koyomi-add.cgi", { command:com, code:code, yyyy_mm_dd:yyyy_mm_dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, ev:ev, eu:eu, carry_on:carry_on, origin:origin }, function( data ){ $( "#LF" ).html( data );});
};

// Updating code into Koyomi
const saveKoyomiAdd = function( com, code, origin ){
	const yyyy_mm_dd = document.getElementById( "yyyy_mm_dd" ).value;
	const tdiv = document.getElementById( "tdiv" ).value;
	const hh_mm = document.getElementById( "hh_mm" ).value;
	const meal_time = document.getElementById( "meal_time" ).value;
	const ev = document.getElementById( "ev" ).value;
	const eu = document.getElementById( "eu" ).value;
	let carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
	let copy = 0;
	if( document.getElementById( "copy" )){
		if( document.getElementById( "copy" ).checked ){ copy = 1; }
	}
	$.post( kp + "koyomi-add.cgi", { command:com, code:code, yyyy_mm_dd:yyyy_mm_dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, ev:ev, eu:eu, carry_on:carry_on, origin:origin, copy:copy }, function( data ){
		$( "#LF" ).html( data );
	});
};

// Saving code into Koyomi direct
const saveKoyomiAdd_direct = function( code, yyyy, mm, dd, tdiv, origin ){
	const hh_mm = document.getElementById( "hh_mm" ).value;
	const meal_time = document.getElementById( "meal_time" ).value;
	const ev = document.getElementById( "ev" ).value;
	const eu = document.getElementById( "eu" ).value;
	let carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
	$.post( kp + "koyomi-add.cgi", { command:"save", code:code, yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, ev:ev, eu:eu, carry_on:carry_on, origin:origin }, function( data ){
			$( "#LF" ).html( data );
	});
};

// Modifying or copying code in Koyomi
const k2Koyomi_direct = function( com, code, yyyy, mm, dd, tdiv, origin ){
	const hh_mm = document.getElementById( "hh_mm" ).value;
	const meal_time = document.getElementById( "meal_time" ).value;
	const ev = document.getElementById( "ev" ).value;
	const eu = document.getElementById( "eu" ).value;
	let carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
 	let copy = 0;
 	if( document.getElementById( "copy" ).checked ){ copy = 1; }
	$.post( kp + "koyomi-add.cgi", { command:com, code:code, yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, ev:ev, eu:eu, carry_on:carry_on, origin:origin, copy:copy }, function( data ){
		$( "#LF" ).html( data );
	});
};


// Modifying or copying fix code in Koyomi
var modifysaveKoyomiFC = function( code, origin ){
	$.post( kp + "koyomi-add.cgi", { command:"move_fix", code:code, origin:origin, copy:1 }, function( data ){
		$( "#LF" ).html( data );

		pushBW();
		dlf = true;
		displayBW();
	});
};

// Return from Koyomi
var koyomiReturn = function(){
	pullBW();
	displayBW();
};

// Return from Koyomi to Koyomi edit
var koyomiReturn2KE = function( yyyy, mm, dd ){
	$.post( kp + "koyomi-edit.cgi", { command:'init', yyyy:yyyy, mm:mm, dd:dd }, function( data ){
		$( "#L2" ).html( data );

		pullBW();
		displayBW();
	});
};

// Koyomi modify or copy panel
var modifyKoyomi = function( com, code, yyyy, mm, dd, tdiv, hh_mm, meal_time, ev, eu, order ){
	$.post( kp + "koyomi-add.cgi", {command:com, code:code, yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv, hh_mm:hh_mm, meal_time, ev:ev, eu:eu, order:order }, function( data ){
		$( "#LF" ).html( data );

		pushBW();
		dl2 = false;
		dlf = true;
		displayBW();
	});
};

// Koyomi insert panel change  for fix code
var modifychangeKoyomiFC = function( code, origin ){
	var carry_on = 1;
	$.post( kp + "koyomi-add.cgi", { command:"modify", code:code, carry_on:carry_on, origin:origin }, function( data ){
		$( "#LF" ).html( data );

		dl2 = false;
		dlf = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Koyomi menu copy / move //////////////////////////////////////////////////////////////

var cmmKoyomi = function( cm_mode, yyyy, mm, dd, tdiv ){
	$.post( kp + "koyomi-cmm.cgi", { command:"init", cm_mode:cm_mode, yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv }, function( data ){
		$( "#LF" ).html( data );

		pushBW();
		flashBW();
		dlf = true;
		dline = true;
		displayBW();
	});
};

var cmmChangeKoyomi = function( cm_mode, origin ){
	var yyyy_mm_dd = document.getElementById( "yyyy_mm_dd" ).value;
	var tdiv = document.getElementById( "tdiv_cmm" ).value;
	var hh_mm = document.getElementById( "hh_mm_cmm" ).value;
	var meal_time = document.getElementById( "meal_time_cmm" ).value;
	var carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
	$.post( kp + "koyomi-cmm.cgi", { command:"init", cm_mode:cm_mode, yyyy_mm_dd:yyyy_mm_dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, carry_on:carry_on, origin:origin }, function( data ){ $( "#LF" ).html( data );});
};

var cmmSaveKoyomi = function( cm_mode, origin ){
	var yyyy_mm_dd = document.getElementById( "yyyy_mm_dd" ).value;
	var tdiv = document.getElementById( "tdiv_cmm" ).value;
	var hh_mm = document.getElementById( "hh_mm_cmm" ).value;
	var meal_time = document.getElementById( "meal_time_cmm" ).value;
	var carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
	$.post( kp + "koyomi-cmm.cgi", { command:"save", cm_mode:cm_mode, yyyy_mm_dd:yyyy_mm_dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, carry_on:carry_on, origin:origin }, function( data ){ $( "#LF" ).html( data );});
};

var cmmSaveKoyomi_direct = function( cm_mode, yyyy, mm, dd, tdiv, origin ){
	var hh_mm = document.getElementById( "hh_mm_cmm" ).value;
	var meal_time = document.getElementById( "meal_time_cmm" ).value;
	var carry_on = 0;
	if( document.getElementById( "carry_on" ).checked ){ carry_on = 1; }
	$.post( kp + "koyomi-cmm.cgi", { command:"save", cm_mode:cm_mode, yyyy:yyyy, mm:mm, dd:dd, tdiv:tdiv, hh_mm:hh_mm, meal_time:meal_time, carry_on:carry_on, origin:origin }, function( data ){ $( "#LF" ).html( data );});
};


/////////////////////////////////////////////////////////////////////////////////
// Koyomi EX //////////////////////////////////////////////////////////////

// Koyomi EX init
var initKoyomiex = function(){
	$.post( kp + "koyomiex.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		dline = true;
		displayBW();
	});
};

// Uploading table file
const importkoyomiex = function(){
	form_data = new FormData( $( '#table_form' )[0] );
	form_data.append( 'command', 'upload' );
	$.ajax( kp + "koyomiex-in.cgi",
		{
			type: 'post',
			processData: false,
			contentType: false,
			data: form_data,
			dataype: 'html',
			success: function( data ){
				$( "#L2" ).html( data )

				dl1 = false;
				dl2 = true;
				dline = true;
				displayBW();
			;}
		}
	);
};


/////////////////////////////////////////////////////////////////////////////////
// Koyomi calc //////////////////////////////////////////////////////////////

// Initiation
var initKoyomiCalc = function(){
	$.post( kp + "koyomi-calc.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dline = true;
		dl1 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Koyomi composition //////////////////////////////////////////////////////////////

// Koyomi composition
var initKoyomiCompo = function(){
	$.post( kp + "koyomi-compo.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dline= true;
		dl1 = true;
		displayBW();
	});
};

// Analysis composition
var calcKoyomiCompo = function(){
	var yyyymmdds = document.getElementById( "yyyymmdds" ).value;
	var yyyymmdde = document.getElementById( "yyyymmdde" ).value;
	if( document.getElementById( "ew_mode" ).checked ){ var ew_mode = 1; }else{ var ew_mode = 0; }
	$.post( kp + "koyomi-compo.cgi", { command:"compo", yyyymmdds:yyyymmdds, yyyymmdde:yyyymmdde, ew_mode:ew_mode }, function( data ){ $( "#L1" ).html( data ); });
};

/////////////////////////////////////////////////////////////////////////////////
// Ginmi //////////////////////////////////////////////////////////////

// Ginmi init
const initGinmi = function(){
	flashBW();
	$.post( "ginmi.cgi", { mod:'menu' }, function( data ){
		$( "#LINE" ).html( data );

	});
	$.post( "ginmi.cgi", { mod:'' }, function( data ){
		$( "#L1" ).html( data );
	});

	dline = true;
	dl1 = true;
	displayBW();
};

/////////////////////////////////////////////////////////////////////////////////
// Physique //////////////////////////////////////////////////////////////

// Physique init
var initPhysique = function(){
	flashBW();
	$.post( "physique.cgi", { mod:'menu' }, function( data ){
		$( "#LINE" ).html( data );

		dline = true;
		displayBW();
	});
	$.post( "physique.cgi", { mod:'' }, function( data ){
		$( "#L1" ).html( data );

		dl1 = true;
		displayBW();
	});
};



/////////////////////////////////////////////////////////////////////////////////
// Mother and child //////////////////////////////////////////////////////////////

// Mother and child init
const initMomChai = function(){
	flashBW();
	$.post( "momchai.cgi", { mod:'menu' }, function( data ){
		$( "#LINE" ).html( data );

	});
	$.post( "momchai.cgi", { mod:'' }, function( data ){
		$( "#L1" ).html( data );

	});

	dline = true;
	dl1 = true;
	displayBW();
};

/////////////////////////////////////////////////////////////////////////////////
// Elderly //////////////////////////////////////////////////////////////

// Elderly init
var initElderly = function(){

};


/////////////////////////////////////////////////////////////////////////////////
// Pathology //////////////////////////////////////////////////////////////

// Pathology init
var initPathology = function(){

};


/////////////////////////////////////////////////////////////////////////////////
// Note //////////////////////////////////////////////////////////////

// Note book
const initNote = function(){
	$.post( "note.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};

// Note book
const writeNote = function(){
	const note = document.getElementById( "note" ).value;
	if( note != '' ){
		$.post( "note.cgi", { command:'write', note:note }, function( data ){ $( "#L1" ).html( data );});
	}
};

// Note book
const deleteNote = function( code ){
	if( document.getElementById( code ).checked ){
		$.post( "note.cgi", { command:'delete', code:code, base:'note', secure:'1' }, function( data ){
			$( "#L1" ).html( data );}
		);
		displayVIDEO( 'Deleted' );
	}else{
		displayVIDEO( 'Check!(>_<)' );
	}
};


/////////////////////////////////////////////////////////////////////////////////
// FCZ edit //////////////////////////////////////////////////////////////

// FCZ list init
var initFCZlist = function(){
	$.post( "fcz-list.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


// FCZ editor
var initFCZedit = function( fcz_code ){
	var base = document.getElementById( "base_select" ).value;
	$.post( "fcz-edit.cgi", { command:'init', base:base, fcz_code:fcz_code }, function( data ){
		$( "#L2" ).html( data );

		dl1 = false;
		dl2 = true;
		displayBW();
	});
};


// FCZ editor save
var saveFCZedit = function( fcz_code ){
	var base = document.getElementById( "base" ).value;
	var fcz_name = document.getElementById( "fcz_name" ).value;
	var origin = document.getElementById( "origin" ).value;

	var ENERC = document.getElementById( "zENERC" ).value;
	var ENERC_KCAL = document.getElementById( "zENERC_KCAL" ).value;
	var WATER = document.getElementById( "zWATER" ).value;

	var PROTCAA = document.getElementById( "zPROTCAA" ).value;
	var PROT = document.getElementById( "zPROT" ).value;
	var PROTV = document.getElementById( "zPROTV" ).value;
	var FATNLEA = document.getElementById( "zFATNLEA" ).value;
	var CHOLE = document.getElementById( "zCHOLE" ).value;
	var FAT = document.getElementById( "zFAT" ).value;
	var FATV = document.getElementById( "zFATV" ).value;
	var CHOAVLM = document.getElementById( "zCHOAVLM" ).value;
	var CHOAVL = document.getElementById( "zCHOAVL" ).value;
	var CHOAVLDF = document.getElementById( "zCHOAVLDF" ).value;
	var CHOV = document.getElementById( "zCHOV" ).value;
	var FIB = document.getElementById( "zFIB" ).value;
	var POLYL = document.getElementById( "zPOLYL" ).value;
	var CHOCDF = document.getElementById( "zCHOCDF" ).value;
	var OA = document.getElementById( "zOA" ).value;

	var ASH = document.getElementById( "zASH" ).value;
	var NA = document.getElementById( "zNA" ).value;
	var K = document.getElementById( "zK" ).value;
	var CA = document.getElementById( "zCA" ).value;
	var MG = document.getElementById( "zMG" ).value;
	var P = document.getElementById( "zP" ).value;
	var FE = document.getElementById( "zFE" ).value;
	var ZN = document.getElementById( "zZN" ).value;
	var CU = document.getElementById( "zCU" ).value;
	var MN = document.getElementById( "zMN" ).value;
	var ID = document.getElementById( "zID" ).value;
	var SE = document.getElementById( "zSE" ).value;
	var CR = document.getElementById( "zCR" ).value;
	var MO = document.getElementById( "zMO" ).value;

	var RETOL = document.getElementById( "zRETOL" ).value;
	var CARTA = document.getElementById( "zCARTA" ).value;
	var CARTB = document.getElementById( "zCARTB" ).value;
	var CRYPXB = document.getElementById( "zCRYPXB" ).value;
	var CARTBEQ = document.getElementById( "zCARTBEQ" ).value;
	var VITA_RAE = document.getElementById( "zVITA_RAE" ).value;
	var VITD = document.getElementById( "zVITD" ).value;
	var TOCPHA = document.getElementById( "zTOCPHA" ).value;
	var TOCPHB = document.getElementById( "zTOCPHB" ).value;
	var TOCPHG = document.getElementById( "zTOCPHG" ).value;
	var TOCPHD = document.getElementById( "zTOCPHD" ).value;
	var VITK = document.getElementById( "zVITK" ).value;

	var THIA = document.getElementById( "zTHIA" ).value;
	var RIBF = document.getElementById( "zRIBF" ).value;
	var NIA = document.getElementById( "zNIA" ).value;
	var NE = document.getElementById( "zNE" ).value;
	var VITB6A = document.getElementById( "zVITB6A" ).value;
	var VITB12 = document.getElementById( "zVITB12" ).value;
	var FOL = document.getElementById( "zFOL" ).value;
	var PANTAC = document.getElementById( "zPANTAC" ).value;
	var BIOT = document.getElementById( "zBIOT" ).value;
	var VITC = document.getElementById( "zVITC" ).value;

	var ALC = document.getElementById( "zALC" ).value;
	var NACL_EQ = document.getElementById( "zNACL_EQ" ).value;

	var FASAT = document.getElementById( "zFASAT" ).value;
	var FAMS = document.getElementById( "zFAMS" ).value;
	var FAPU = document.getElementById( "zFAPU" ).value;
	var FAPUN3 = document.getElementById( "zFAPUN3" ).value;
	var FAPUN6 = document.getElementById( "zFAPUN6" ).value;

	var FIBTG = document.getElementById( "zFIBTG" ).value;
	var FIBSOL = document.getElementById( "zFIBSOL" ).value;
	var FIBINS = document.getElementById( "zFIBINS" ).value;
	var FIBTDF = document.getElementById( "zFIBTDF" ).value;
	var FIBSDFS = document.getElementById( "zFIBSDFS" ).value;
	var FIBSDFP = document.getElementById( "zFIBSDFP" ).value;
	var FIBIDF = document.getElementById( "zFIBIDF" ).value;
	var STARES = document.getElementById( "zSTARES" ).value;

	$.post( "fcz-edit.cgi", {
		command:'save', fcz_code:fcz_code, base:base, fcz_name:fcz_name, origin:origin, food_code:null, food_name:null, food_weight:100,
		ENERC:ENERC, ENERC_KCAL:ENERC_KCAL, WATER:WATER,
		PROTCAA:PROTCAA, PROT:PROT, PROTV:PROTV, FATNLEA:FATNLEA, CHOLE:CHOLE, FAT:FAT, FATV:FATV, CHOAVLM:CHOAVLM, CHOAVL:CHOAVL, CHOAVLDF:CHOAVLDF, CHOV:CHOV, FIB:FIB, POLYL:POLYL, CHOCDF:CHOCDF, OA:OA,
		ASH:ASH, NA:NA, K:K, CA:CA, MG:MG, P:P, FE:FE, ZN:ZN, CU:CU, MN:MN, ID:ID, SE:SE, CR:CR, MO:MO,
		RETOL:RETOL, CARTA:CARTA, CARTB:CARTB, CRYPXB:CRYPXB, CARTBEQ:CARTBEQ, VITA_RAE:VITA_RAE, VITD:VITD, TOCPHA:TOCPHA, TOCPHB:TOCPHB, TOCPHG:TOCPHG, TOCPHD:TOCPHD, VITK:VITK,
		THIA:THIA, RIBF:RIBF, NIA:NIA, NE:NE, VITB6A:VITB6A, VITB12:VITB12, FOL:FOL, PANTAC:PANTAC, BIOT:BIOT, VITC:VITC,
		ALC:ALC, NACL_EQ:NACL_EQ,
		FASAT:FASAT, FAMS:FAMS, FAPU:FAPU, FAPUN3:FAPUN3, FAPUN6:FAPUN6,
		FIBTG:FIBTG, FIBSOL:FIBSOL, FIBINS:FIBINS, FIBTDF:FIBTDF, FIBSDFS:FIBSDFS, FIBSDFP:FIBSDFP, FIBIDF:FIBIDF, STARES:STARES
	}, function( data ){
//			$( "#L2" ).html( data );
		$.post( "fcz-list.cgi", { command:'init', base:base }, function( data ){
			$( "#L1" ).html( data );

			dl1 = true;
			dl2 = false;
			displayBW();
			displayVIDEO( 'saved' );
		});

	});
};


/////////////////////////////////////////////////////////////////////////////////
// Ref instake //////////////////////////////////////////////////////////////

// Ref instake init
const initRefIntake = function(){
	$.post( "ref-intake.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};
