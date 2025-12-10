// Nutorition Browser 2020 core.js 0.7.2 (2025/07/26)
///////////////////////////////////////////////////////////////////////////////////
// Global ////////////////////////////////////////////////////////////////////
dl1 = false;
dl2 = false;
dl3 = false;
dl4 = false;
dl5 = false;
dlf = false;
dline = false;

hl1 = false;
hl2 = false;
hl3 = false;
hl4 = false;
hl5 = false;
hlf = false;
hline = false;

world = null
bwl1 = null;
bwl2 = null;
bwl3 = null;
bwl4 = null;
bwl5 = null;
bwlf = null;
line = null;
video = null;

help = null;
help_tp = '1154';

menu_status = 0;
general_ = '';


/////////////////////////////////////////////////////////////////////////////////
// Paging /////////////////////////////////////////////////////////////////////////

// initialization
window.onload = function(){
	if( !!document.getElementById( "L1" )){
		world = document.getElementById( "WORLD" );
		bwl1 = document.getElementById( "L1" );
		bwl2 = document.getElementById( "L2" );
		bwl3 = document.getElementById( "L3" );
		bwl4 = document.getElementById( "L4" );
		bwl5 = document.getElementById( "L5" );
		bwlf = document.getElementById( "LF" );
		line = document.getElementById( "LINE" );
		video = document.getElementById( "VIDEO" );
		help = document.getElementById( "HELP" );

		toHelp();
	}
};


// Closing browse windows
// This feature will be discontinued in the future.
closeBroseWindows = function( num ){
	switch( Number( num )){
	case 0: document.getElementById( "L1" ).style.display = 'none';
	case 1: document.getElementById( "L2" ).style.display = 'none';
	case 2: document.getElementById( "L3" ).style.display = 'none';
	case 3: document.getElementById( "L4" ).style.display = 'none';
	case 4: document.getElementById( "L5" ).style.display = 'none';
	case 5: document.getElementById( "LF" ).style.display = 'none';
 	}
}


// Reopening browse windows
displayBW = function(){
	if( dl1 ){ bwl1.style.display = 'block'; }else{ bwl1.style.display = 'none'; }
	if( dl2 ){ bwl2.style.display = 'block'; }else{ bwl2.style.display = 'none'; }
	if( dl3 ){ bwl3.style.display = 'block'; }else{ bwl3.style.display = 'none'; }
	if( dl4 ){ bwl4.style.display = 'block'; }else{ bwl4.style.display = 'none'; }
	if( dl5 ){ bwl5.style.display = 'block'; }else{ bwl5.style.display = 'none'; }
	if( dlf ){ bwlf.style.display = 'block'; }else{ bwlf.style.display = 'none'; }
	if( dline ){ line.style.display = 'block'; }else{ line.style.display = 'none'; }
}


// Resetting level status
flashBW = function(){
	dl1 = false;
	dl2 = false;
	dl3 = false;
	dl4 = false;
	dl5 = false;
	dlf = false;
	dline = false;
}


// Pushing level status to hide
pushBW = function(){
	hl1 = dl1;
	hl2 = dl2;
	hl3 = dl3;
	hl4 = dl4;
	hl5 = dl5;
	hlf = dlf;
	hline = dline;
}


// Pulling level status from hide
pullBW = function(){
	dl1 = hl1;
	dl2 = hl2;
	dl3 = hl3;
	dl4 = hl4;
	dl5 = hl5;
	dlf = hlf;
	dline = hline;
}


// Opning menu LINE
// This feature will be discontinued in the future.
displayLINE = function( msg ){
	if( msg == 'on' ){
		line.style.display = 'block';
	}else if( msg == 'off' ){
		line.style.display = 'none';
	}else{
		line.style.display = 'block';
		line.innerHTML = msg;
	}
}


// Displaying message on VIDEO
displayVIDEO = function( msg ){
	video.innerHTML = msg;
	video.style.display = 'block';
	video.style.color = 'lime';
	var fx = function(){
		video.innerHTML = "";
		video.style.display = 'none';
	};
	setTimeout( fx, 2000 );
}


// Displaying message on VIDEO rec mode
displayREC = function(){
	video.innerHTML = "●";
	video.style.display = 'block';
	video.style.color = 'orangered';
	var fx = function(){
		video.innerHTML = "";
		video.style.display = 'none';
	};
	setTimeout( fx, 1000 );
}


// Exchanging menu sets
changeMenu = function( user_status ){
	switch( menu_status ){
		case 0:
			document.getElementById( "guild_menu" ).style.display = 'inline';
			displayVIDEO( 'Guild menu' );
			if( user_status >= 5 && user_status != 6 ){ menu_status = 1; }else{ menu_status = 3; }
			break;
		case 1:
			document.getElementById( "guild_menu" ).style.display = 'none';
			document.getElementById( "gs_menu" ).style.display = 'inline';
			displayVIDEO( 'Guild Shun menu' );
			if( user_status >= 8 ){ menu_status = 2; }else{ menu_status = 3; }
			break;
		case 2:
			document.getElementById( "gs_menu" ).style.display = 'none';
			document.getElementById( "gm_menu" ).style.display = 'inline';
			displayVIDEO( 'GM menu' );
			menu_status = 3;
			break;
		case 3:
			document.getElementById( "guild_menu" ).style.display = 'none';
			document.getElementById( "gs_menu" ).style.display = 'none';
			document.getElementById( "gm_menu" ).style.display = 'none';
			displayVIDEO( 'Standard menu' );
			menu_status = 0;
			break;
	}
}


// changing help to
toHelp = function( page ){
	if( page==null ){
		help.innerHTML = "<a href='https://bacura.jp/?page_id=" + help_tp + "' target='manual'><img src='bootstrap-dist/icons/question-circle-gray.svg' style='height:3em; width:2em;'></a>";
	}else{
		help.innerHTML = "<a href='https://bacura.jp/?page_id=" + page + "'' target='manual'><img src='bootstrap-dist/icons/question-circle-ndsk.svg' style='height:3em; width:2em;'></a>";
	}
}



/////////////////////////////////////////////////////////////////////////////////
// Photo to modal /////////////////////////////////////////////////////////////////////////

const modalPhoto = function( code ){
	$.post( "photo.cgi", { command:'modal_body', code:code }, function( data ){
		$( "#modal_body" ).html( data );
		$.post( "photo.cgi", { command:'modal_label', code:code }, function( data ){
			$( "#modal_label" ).html( data );
			$( '#modal' ).modal( 'show' );
		});
	});
}


/////////////////////////////////////////////////////////////////////////////////
// Post to layler /////////////////////////////////////////////////////////////////////////

const postLayer = async ( script, command, transition, layer, requestData, successCallback ) => {
    try {
        const response = await fetch( script, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ command, ...requestData }),
        });
        if ( !response.ok ) {
            const text = await response.text();
            console.error( `Request failed: HTTP ${response.status}, ${text}` );
            alert( "An error occurred. Please try again." );
            return;
        }
        const responseData = await response.text();
        if( transition ){
			const element = document.getElementById( layer );
			element.innerHTML = responseData;
        }
    } catch ( error ) {
        console.error( 'Request failed:', error );
        alert( "An error occurred. Please try again." );
    }
};


// Get all DOM fields
const getDOMdata = function( fieldList, prefix ){
	let data = {};
	fieldList.forEach( field => {
		data[field] = document.getElementById( prefix + field ).value;
	});

	return data;
};



/////////////////////////////////////////////////////////////////////////////////
// Browsing nutritional Information /////////////////////////////////////////////////////////////////////

// Display foods on BWL1
var summonL1 = function( num ){
	$.get( "square.cgi", { channel:"fctb", category:num }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


// Display foods on BWL2
var summonL2 = function( key ){
	$.get( "square.cgi", { channel:"fctb_l2", food_key:key }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


// Display foods on BWL3
var summonL3 = function( key, direct ){
	if( direct > 0 ){ closeBroseWindows( direct ); }
	$.get( "square.cgi", { channel:"fctb_l3", food_key:key }, function( data ){
		$( "#L3" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		dl3 = true;
		displayBW();
	});
};


// Display foods on BWL4
var summonL4 = function( key, direct ){
	if( direct > 0 ){ closeBroseWindows( direct ); }
	$.get( "square.cgi", { channel:"fctb_l4", food_key:key }, function( data ){
		$( "#L4" ).html( data );

		dl4 = true;
		dl5 = false;
		dlf = false;
		displayBW();
	});
};


//////////////////////////////////////////////////////////////////////////////////
// Browsing nutritional Information subset ///////////////////////////////////////////////////////////////////////

// Display foods on BWL5
const viewDetailSub = function( com, key, direct ){
	if( direct > 0 ){ closeBroseWindows( direct ); }
	$.post( "detail-sub.cgi", { command:com, food_key:key }, function( data ){ $( "#L5" ).html( data );});
	dl5 = true;
	dlf = false;
	displayBW();
};


// Changing weight of food
const changeDSWeight = function( com, key, fn ){
	const fraction_mode = document.getElementById( "fraction" ).value;
	const weight = document.getElementById( "weight" ).value;
	$.post( "detail-sub.cgi", { command:com, food_key:key, frct_mode:fraction_mode, food_weight:weight, food_no:fn }, function( data ){
		$( "#L5" ).html( data );
		displayVIDEO( '(>_<)' );

	});
};


//////////////////////////////////////////////////////////////////////////////////
// Browsing nutritional Information (ditail) ///////////////////////////////////////////////////////////////////////

// Display ditail information on LF
const detailView = function( fn ){
	var fraction_mode = document.getElementById( "fraction" ).value;
	var food_weight = document.getElementById( "weight" ).value;
	$.post( "detail.cgi", { command:'init', food_no:fn, frct_mode:fraction_mode, food_weight:food_weight, selectu:'g' }, function( data ){
		$( "#LF" ).html( data );

		pushBW();
		dl5 = false;
		dlf = true;
		displayBW();
	});
};

// Display ditail information on LF (history)
const detailView_his = function( fn ){
	$.post( "detail.cgi", { command:'init', food_no:fn, frct_mode:1, food_weight:100, selectu:'g' }, function( data ){
		$( "#LF" ).html( data );

		pushBW();
		dline = false;
		dl1 = false;
		dlf = true;
		displayBW();
	});
};

// Display sub-foods
const cb_detail_sub = ( key, weight, base_fn ) => {
	$.post( "detail-sub.cgi", { command:"cb", food_key:key, frct_mode:0, food_weight:weight, base:'cb', base_fn:base_fn }, data => {
		$( "#L2" ).html( data );
		flashBW();
		dl2 = true;
		displayBW();
	});
};

// Display para-foods
const cb_detail_para = ( key, weight, base_fn ) => {
	$.post( "detail-para.cgi", { command:"cb", food_key:key, frct_mode:0, food_weight:weight, base:'cb', base_fn:base_fn }, data => {
		$( "#L3" ).html( data );
		flashBW();
		dl3 = true;
		displayBW();
	});
};

// Change juten in para-foods
const cb_detail_para_juten = ( key, weight, base_fn ) => {
	const juten = $( "input[name='para_juten']:checked" ).val() || "FLAT";
	$.post( "detail-para.cgi", { command:"cb", food_key:key, frct_mode:0, food_weight:weight, base:'cb', base_fn,juten }, data => $( "#L3" ).html( data ));
};


/////////////////////////////////////////////////////////////////////////////////
// Referencing /////////////////////////////////////////////////////////////////////////

// Disply results
const search = function(){
	const words = document.getElementById( "words" ).value;
	const qcate = document.getElementById( "qcate" ).value;
	if( words != '' ){
		flashBW();
		switch( qcate ){
		case '0':
			$.post( "search-food.cgi", { words:words }, function( data ){
				$( "#L1" ).html( data );
		 		dl1 = true;
		 		displayBW();
			});
			break;
		case '1':
			$.post( "recipel.cgi", { command:'refer', words:words }, function( data ){
				$( "#L1" ).html( data );
		 		dl1 = true;
		 		displayBW();
			});
			break;
		case '2':
			$.post( "memory.cgi", { command:'refer', words:words, depth:1 }, function( data ){
				$( "#L1" ).html( data );
		 		dl1 = true;
		 		pushBW();
		 		displayBW();
			});
			break;
 		}
	}
};

// Direct recipe search
var searchDR = function( words ){
	$.post( "recipel.cgi", { command:'refer', words:words }, function( data ){
		$( "#L1" ).html( data );

		words = document.getElementById( "words" ).value = words;
		qcate = document.getElementById( "qcate" ).value = 1;

	 	flashBW();
	 	dl1 = true;
	 	displayBW();
	});
};

// Sending alias request
var aliasRequest = function( food_no ){
	document.getElementById( "LF" ).style.display = 'block';
	var alias = document.getElementById( "alias" ).value;
	if( alias != '' && alias != general_ ){
		$.post( "alias-req.cgi", { food_no:food_no, alias:alias }, function( data ){
			displayVIDEO( 'Request sent' );
		});
	}else if( alias == general_ ){
		displayVIDEO( 'Request sent' );
	}else{
		displayVIDEO( 'Alias! (>_<)' );
	}
	general_ = alias;
};


// Copy to words
cp2words = function( words, qcate ){
	document.getElementById( "words" ).value = words;
	if( qcate != '' ){ document.getElementById( "qcate" ).value = qcate; }
	$( '#modal_tip' ).modal( 'hide' );
	displayVIDEO( 'Picked' );
};


/////////////////////////////////////////////////////////////////////////////////
// history /////////////////////////////////////////////////////////////////////////
const initHistory = function( com ){
	flashBW();
	
	$.post( "history.cgi", { command:'menu' }, function( data ){
		$( "#LINE" ).html( data );
	});
	$.post( "history.cgi", { command:com, sub_fg:'init' }, function( data ){
		$( "#L1" ).html( data );
	});

	dline = true;
	dl1 = true;
	displayBW();
	pushBW();
};


/////////////////////////////////////////////////////////////////////////////////
// Puseudo food //////////////////////////////////////////////////////////////////////

const pseudoAdd = function( com, food_key, food_no ){
	$.post( "pseudo.cgi", { command:com, food_key:food_key, food_no:food_no }, function( data ){
		$( "#LF" ).html( data );

		dlf = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Bookshelf /////////////////////////////////////////////////////////////////////////

var bookOpen = function( url, depth ){
	dline = false;
	displayBW();

	closeBroseWindows( depth );
	$.ajax({ url:url, type:'GET', dataType:'html', success:function( data ){ $( "#L" + depth ).html( data ); }});
	document.getElementById( "L" + depth ).style.display = 'block';
};


/////////////////////////////////////////////////////////////////////////////////
// Memory list ///////////////////////////////////////////////////////////////////////

const initMemoryList = function(){
	$.post( "memory-list.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Memory edit///////////////////////////////////////////////////////////////////////

// Add new memory
const newMemory = function( category_, pointer, mode ){
	let category = category_
	if( category_ == '' && mode == 'refer' ){ category = document.getElementById( 'ref_new_categoly' ).value; }
	$.post( "memory-edit.cgi", { command:'new', category:category, pointer:pointer, mode:mode, depth:2 }, function( data ){
		$( "#LF" ).html( data );
		pushBW();
		flashBW();
		dlf = true;
		displayBW();
	});
};

const editMemory = function( code, mode ){
	$.post( "memory-edit.cgi", { command:'edit', code:code, mode:mode, depth:2 }, function( data ){
		$( "#LF" ).html( data );
		pushBW();
		flashBW();
		dlf = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Memory ///////////////////////////////////////////////////////////////////////

// Open memory
const memoryOpen = function( code ){
	$.post( "memory.cgi", { command:'refer', code, depth:2 }, function( data ){
		$( "#L2" ).html( data );

		dl2 = true;
		pushBW();
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Meta data //////////////////////////////////////////////////////////////////////////

var metaDisplay = function( com ){
	$.post( "meta.cgi", { command:com }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Proprty //////////////////////////////////////////////////////////////////////////

// Display config menu
var configInit = function(){
	flashBW();
	$.post( "config.cgi", { mod:'menu' }, function( data ){
		$( "#LINE" ).html( data );
		dline = true;
		displayBW();
	});
	$.post( "config.cgi", { mod:'' }, function( data ){
		$( "#L1" ).html( data );
		dl1 = true;
		displayBW();
	});
};

// Display config form
var configForm = function( mod ){
	$.post( "config.cgi", { mod:mod }, function( data ){ $( "#L1" ).html( data );});
};


/////////////////////////////////////////////////////////////////////////////////
// Modal Photo viewer //////////////////////////////////////////////////////////////////////////

const modalPhotoOn = function( code ){
	$.post( "photo.cgi", { command:'modal', code:code }, function( data ){
		$( '#MODAL' ).html( data );
	});
};

////////////////////////////////////////////////////////////////////////////////////////
// Chopping boad interface////////////////////////////////////////////////////////////////////////

// Add food into sum, and reload CB counter
const addingCB = function( fn, weight_id, food_name ){

	displayVIDEO( weight_id );
	if( weight_id != '' ){
		var weight = document.getElementById( weight_id ).value;
	}
	$.post( "cboardm.cgi", { food_no:fn, food_weight:weight, mode:'add' }, function( data ){
		$( "#CBN" ).html( data );
		if( fn != '' ){ displayVIDEO( '+' + food_name ); }

		if( weight_id == 'weight_sub' ){
			initCB( 'init' );

			flashBW();
			dl1 = true;
			displayBW();
		}
	});
};


// Only reload CB number
const refreshCBN = function(){
	$.post( "cboardm.cgi", { mode:'refresh' }, function( data ){ $( "#CBN" ).html( data );});
};


////////////////////////////////////////////////////////////////////////////////////////
// Chopping boad ////////////////////////////////////////////////////////////////////////

// Display CB sum
const initCB = function( com, code, recipe_user ){
	if( com == 'reload' ){
		$.post( "cboard.cgi", { command:'reload', code:code }, function( data ){
			$( "#L1" ).html( data );
		});
	}else{
		$.post( "cboard.cgi", { command:com, code:code, recipe_user:recipe_user }, function( data ){
			$( "#L1" ).html( data );

			flashBW();
			dl1 = true;
			displayBW();
			setTimeout( refreshCBN(), 2000 );
		});
	}
};

// Exchange food in sum
const changingCB = function( fn, base_fn, weight ){
	if( fn !='' ){
		$.post( "cboardm.cgi", { food_no:fn, food_weight:weight, base_fn:base_fn, mode:'change' }, function( data ){
			$( "#CBN" ).html( data );
			displayREC();

			$.post( "cboard.cgi", { command:'refresh', code:'' }, function( data ){
				$( "#L1" ).html( data );

				flashBW();
				dl1 = true;
				displayBW();
			});
		});
	}
};



////////////////////////////////////////////////////////////////////////////////
// Recipe editor ////////////////////////////////////////////////////////////////////////

const recipeEdit = function( com, code ){
	$.post( "recipe.cgi", { command:com, code:code }, function( data ){
		$( "#L2" ).html( data );
		dl2 = true;
		displayBW();
	});
};


////////////////////////////////////////////////////////////////////////////////////
// Recipe list ////////////////////////////////////////////////////////////////////////

const recipeList = function( com ){
	$.post( "recipel.cgi", { command:com }, function( data ){
		$( "#L1" ).html( data );
		if( com == 'reset'){ document.getElementById( "words" ).value = ''; }

		flashBW();
		dl1 = true;
		displayBW();
	});
};


///////////////////////////////////////////////////////////////////////////////////
// 成分計算 ////////////////////////////////////////////////////////////////////////

// まな板の成分計算表ボタンを押してL2にリストを表示
const calcView = function( code ){
	$.post( "calc.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


///////////////////////////////////////////////////////////////////////////////////
// 原価計算 ////////////////////////////////////////////////////////////////////////

// まな板の原価計算表ボタンを押してL2にリストを表示
var priceView = function( code ){
	$.post( "price.cgi", { command:'view', code:code }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};

// 原価計算表の購入量変更でL2に原価表を更新
var changeFV = function( code, fvid, food_no ){
	var food_volume = document.getElementById( fvid ).value;
	$.post( "price.cgi", { command:'changeFV', code:code, food_volume:food_volume, food_no:food_no }, function( data ){ $( "#L2" ).html( data );});
};

// 原価計算表の支払金額変更でL2に原価表を更新
var changeFP = function( code, fpid, food_no ){
	var food_price = document.getElementById( fpid ).value;
	$.post( "price.cgi", { command:'changeFP', code:code, food_price:food_price, food_no:food_no }, function( data ){ $( "#L2" ).html( data );});
};

// 原価計算表のマスター価格を適用してL2に原価表を更新
var pricemAdpt = function( code ){
	$.post( "price.cgi", { command:'adpt_master', code:code }, function( data ){
		$( "#L2" ).html( data );
		displayVIDEO( 'マスター価格を適用' );
	});
};

// 原価計算表のマスター価格登録（でL2に原価表を更新）
var pricemReg = function( code ){
	$.post( "price.cgi", { command:'reg_master', code:code }, function( data ){
//		$( "#L2" ).html( data );
		displayVIDEO( 'マスター価格に登録' );
	});
};

// 原価計算表の価格を元にレシピの価格区分を変更
var recipeRef = function( code ){
	$.post( "price.cgi", { command:'ref_recipe', code:code }, function( data ){
//		$( "#L2" ).html( data );
		displayVIDEO( '価格区分へ反映' );
	});
};

// 原価計算表の初期化ボタンでL2に原価表を更新
var clearCT = function( code ){
	if( document.getElementById( "clearCT_check" ).checked ){
		$.post( "price.cgi", { command:'clearCT', code:code }, function( data ){ $( "#L2" ).html( data );});
	}else{
		displayVIDEO( '(>_<) check!' );
	}
};

///////////////////////////////////////////////////////////////////////////////////
// Lucky star input ////////////////////////////////////////////////////////////////////////

// Lucky☆入力ボタンを押してL2に入力画面を表示、そしてL1を非表示にする
const luckyInput = function(){
	$.post( "lucky.cgi", { command:'init' }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


///////////////////////////////////////////////////////////////////////////////////
// Foodize ////////////////////////////////////////////////////////////////////////

// 成分計算表の食品化ボタンを押してL3に擬似食品フォームを表示
const Pseudo_R2F = function( code ){
	$.post( "pseudo_r2f.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


///////////////////////////////////////////////////////////////////////////////////
// Print selector /////////////////////////////////////////////////////////////////

const print_templateSelect = function( code ){
	$.post( "print.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );
		$( '#modal_tip' ).modal( 'hide' );

		flashBW();
		dl2 = true;
		displayBW();
	});
};

/////////////////////////////////////////////////////////////////////////////////
// meal tray interface ////////////////////////////////////////////////////////////////////////

// 献立追加ボタンを押してmealにレシピを追加して、まな献立カウンタを増やす
const addingMT = function( recipe_code, recipe_name ){
	$.post( "mtraym.cgi", { mode:'add', recipe_code:recipe_code }, function( data ){
		$( "#MTN" ).html( data );
		$( '#modal_tip' ).modal( 'hide' );

		if( recipe_code != '' ){ displayVIDEO( '+' + recipe_name ); }
	});
};


// Only reload Table number
const refreshMT = function(){
	$.post( "mtraym.cgi", { mode:'refresh' }, function( data ){ $( "#MTN" ).html( data );});
};

/////////////////////////////////////////////////////////////////////////////////
// Food tray interface ////////////////////////////////////////////////////////////////////////

const initMT = function( com, code ){
	$.post( "mtray.cgi", { command:com, code:code }, function( data ){
		$( "#L1" ).html( data );
		if( com == 'init' ){
			flashBW();
			dl1 = true;
			displayBW();
		}
	});
};


////////////////////////////////////////////////////////////////////////////////
// Set menu ////////////////////////////////////////////////////////////////////////

const initMenu = function( code ){
	$.post( "menu.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );
		dl2 = true;
		displayBW();
	});
	$.post( "photo.cgi", { command:'view_series', code:code, base:'menu' }, function( data ){
		$( "#LM" ).html( data )
		dlm = true;
		displayBW();
	});
};


////////////////////////////////////////////////////////////////////////////////////
// Set menu list ////////////////////////////////////////////////////////////////////////

// まな板のレシピ読み込みボタンを押してL1に献立リストを表示
var menuList = function( com ){
	$.post( "menul.cgi", { command:com }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


///////////////////////////////////////////////////////////////////////////////////
// Calculation of menu ////////////////////////////////////////////////////////////////////////

// Calculation of menu
const initCalcMenu = function( code ){
	$.post( "menu-calc.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


///////////////////////////////////////////////////////////////////////////////////
// Analysis of menu ////////////////////////////////////////////////////////////////////////

// Analysis of menu
const menuAnalysis = function( code ){
	$.post( "menu-analysis.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Detective ////////////////////////////////////////////////////////////////////////

//
const initDetective = function(){
	const code = document.getElementById( "words" ).value;

	$.post( "detective.cgi", { command:'init', code:code }, function( data ){
		$( "#L2" ).html( data );

		flashBW();
		dl1 = true;
		dl2 = true;
		displayBW();
	});
};
