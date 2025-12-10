//shun.js ver 0.0.4 (2025/08/22)

/////////////////////////////////////////////////////////////////////////////////
// Cooking school //////////////////////////////////////////////////////////////

//
var initSchool = function(){
	flashBW();
	$.post( "school.cgi", { command:"menu" }, function( data ){
		$( "#LINE" ).html( data );
		dline = true;
		displayBW();
	});
	$.post( "school.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );
		dl1 = true;
		displayBW();
	});
};

// School koyomi change
var changeSchoolk = function(){
	var yyyy_mm = document.getElementById( "yyyy_mm" ).value;
	$.post( "school.cgi", { command:"init", yyyy_mm:yyyy_mm }, function( data ){ $( "#L1" ).html( data );});
};

// School status change
var changeSchoolkSt = function( dd, ampm, status ){
	var yyyy_mm = document.getElementById( "yyyy_mm" ).value;
	$.post( "school.cgi", { command:"changest", yyyy_mm:yyyy_mm, dd:dd, ampm:ampm, status:status }, function( data ){ $( "#L1" ).html( data );});
};

// School open
var openSchoolk = function( dd, ampm ){
	var yyyy_mm = document.getElementById( "yyyy_mm" ).value;
	$.post( "school.cgi", { command:"open", yyyy_mm:yyyy_mm, dd:dd, ampm:ampm }, function( data ){ $( "#L1" ).html( data );});
};

/////////////////////////////////////////////////////////////////////////////////
// Cooking school menu //////////////////////////////////////////////////////////////

// menu
var initSchoolMenu = function(){
	$.post( "school-menu.cgi", { command:"init" }, function( data ){ $( "#L1" ).html( data );});
};

// Making new school menu label group
var mekeSchoolGroup = function(){
	var group_new = document.getElementById( 'group_new' ).value;
	if( group_new != '' ){
		$.post( "school-menu.cgi", { command:"group_new", group_new:group_new }, function( data ){ $( "#L1" ).html( data );});
	}else{
		displayVIDEO( 'Group name! (>_<)' );
	}
};

// Deleting school menu label group
var delSchoolGroup = function( label_group ){
	if(document.getElementById( "del_check_" + label_group ).checked){
		$.post( "school-menu.cgi", { command:"group_del", group_new:label_group }, function( data ){
			$( "#L1" ).html( data );
			displayVIDEO( label_group );
		});
	}else{
		displayVIDEO( 'Check! (>_<)' );
	}
};

// Changing school menu label
var changeSchoolLabel = function( label_group, group_no, label_no ){
	var label_new = document.getElementById( 'label' + group_no + '_' + label_no ).value;
	$.post( "school-menu.cgi", { command:"label_change", label_group:label_group, label_no:label_no, label_new:label_new }, function( data ){
		$( "#L1" ).html( data );
		displayVIDEO( label_new );
	});
};

// Select school menu selector
var selectSchoolMenu = function(){
	var group_select = document.getElementById( 'group_select' ).value;
	var label_select = document.getElementById( 'label_select' ).value;
	var month_select = document.getElementById( 'month_select' ).value;
	var week_select = document.getElementById( 'week_select' ).value;
	$.post( "school-menu.cgi", { command:'menu_select', group_select:group_select, label_select:label_select, month_select:month_select, week_select:week_select }, function( data ){ $( "#L1" ).html( data );});
};


/////////////////////////////////////////////////////////////////////////////////
// Cooking school stock //////////////////////////////////////////////////////////////

// menu
var initSchoolStock = function(){
	$.post( "school-stock.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dline = true;
		dl1 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Cooking school custom //////////////////////////////////////////////////////////////

// custom
var initSchoolCustom = function(){
	$.post( "school-custom.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dline = true;
		dl1 = true;
		displayBW();
	});
};

// Update school code
var saveSchoolCustom = function(){
	var cs_code = document.getElementById( 'cs_code' ).value;
	var cs_name = document.getElementById( 'cs_name' ).value;
	var format = 0;
displayVIDEO( cs_name );
	if( document.getElementById( 'enable0' ).checked ){ var enable0 = 1; }else{ var enable0 = 0; }
	if( document.getElementById( 'enable1' ).checked ){ var enable1 = 1; }else{ var enable1 = 0; }
	if( document.getElementById( 'enable2' ).checked ){ var enable2 = 1; }else{ var enable2 = 0; }
	if( document.getElementById( 'enable3' ).checked ){ var enable3 = 1; }else{ var enable3 = 0; }
	var title0 = document.getElementById( 'title0' ).value;
	var title1 = document.getElementById( 'title1' ).value;
	var title2 = document.getElementById( 'title2' ).value;
	var title3 = document.getElementById( 'title3' ).value;
	var menu_group0 = document.getElementById( 'menu_group0' ).value;
	var menu_group1 = document.getElementById( 'menu_group1' ).value;
	var menu_group2 = document.getElementById( 'menu_group2' ).value;
	var menu_group3 = document.getElementById( 'menu_group3' ).value;
	var document0 = document.getElementById( 'document0' ).value;
	var document1 = document.getElementById( 'document1' ).value;
	var document2 = document.getElementById( 'document2' ).value;
	var document3 = document.getElementById( 'document3' ).value;
	var print_ins = document.getElementById( 'print_ins' ).value;
	var qr_ins = document.getElementById( 'qr_ins' ).value;

	$.post( "school-custom.cgi", { command:"save", cs_code:cs_code, cs_name:cs_name, format:format,
		enable0:enable0, enable1:enable1, enable2:enable2, enable3:enable3,
		title0:title0, title1:title1, title2:title2, title3:title3,
		menu_group0:menu_group0, menu_group1:menu_group1, menu_group2:menu_group2, menu_group3:menu_group3,
		document0:document0, document1:document1, document2:document2, document3:document3,
		print_ins:print_ins, qr_ins:qr_ins
	}, function( data ){ $( "#L1" ).html( data );});
};


/////////////////////////////////////////////////////////////////////////////////
// Management of account M //////////////////////////////////////////////////////////////

// Account list
const initAccountM = function(){
	$.post( "account-mom.cgi", { command:"init" }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


// Changing Account
const chageAccountM = function(){
	var login_mv = document.getElementById( "login_mv" ).value;
	location.href = "login.cgi?mode=family" + "&login_mv=" + login_mv;
}


// Open a recipe print screen
const makeQRpaper = function( uid, uid_d, cn ){
	const url = 'coki/qr-paper.cgi?uid=' + uid + '&uid_d=' + uid_d + '&cn=' + cn;
	window.open( url, 'print' );
	displayVIDEO( 'QR paper on the another tab' );
};


/////////////////////////////////////////////////////////////////////////////////
// Tokei R //////////////////////////////////////////////////////////////

// Tokei R init
var initToker = function(){
	flashBW();
	$.post( "toker.cgi", { mod:'line' }, function( data ){
		$( "#LINE" ).html( data );
		dline = true;
		displayBW();
	});
	$.post( "toker.cgi", { mod:'' }, function( data ){
		$( "#L1" ).html( data );
		dl1 = true;
		displayBW();
	});
};

var tokerForm = function( mod ){
	$.post( "toker.cgi", { mod:mod, command:'form' }, function( data ){ $( "#L1" ).html( data );});
};


/////////////////////////////////////////////////////////////////////////////////
// Nutrition visionnerz //////////////////////////////////////////////////////////////

// Init
var visionnerz = function( yyyymmdd ){
	$.post( "visionnerz.cgi", { command:'init', yyyymmdd:yyyymmdd }, function( data ){
		$( "#L4" ).html( data );

		$.post( "visionnerz.cgi", { command:'raw', yyyymmdd:yyyymmdd }, function( raw ){
			$( "#LF" ).html( raw );

			var column = ( String( raw )).split( ':' );
			var hours = ( String( column[0] )).split(',');
			var d_protein = ( String( column[1] )).split(',');
			var d_protein_ = ( String( column[2] )).split(',');
			var d_fat = ( String( column[3] )).split(',');
			var d_fat_ = ( String( column[4] )).split(',');
			var d_sugars = ( String( column[5] )).split(',');
			var d_sugars_ = ( String( column[6] )).split(',');
			var d_sodium = ( String( column[7] )).split(',');
			var d_potassium = ( String( column[8] )).split(',');
			var d_fiber = ( String( column[9] )).split(',');
			var d_water = ( String( column[10] )).split(',');
			var d_alcohol = ( String( column[11] )).split(',');

			var chart = c3.generate({
				bindto: '#visionnerz-intake',

				data: {
					x: '時間',
					axes: { '水分(g)':'y2', 'ナトリウム(mg)':'y2', 'カリウム(mg)':'y2' },
					columns: [hours, d_protein, d_fat, d_sugars, d_sodium, d_potassium, d_fiber, d_water, d_alcohol]
				},
				axis: {
					x: {
						 label:{text:'時間（時）', position:'outer-center' },
						 tick:{ values: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']}
					},
					y: {
			    		type:'linear', min:0, padding:{bottom:0},
			    		tick:{  values:['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'] },
	 					label:{ text:'たんぱく質 / 脂質 / 糖質 / 食物繊維 / アルコール', position: 'outer-middle' }
					},
					y2: {
						show: true,
			    		type: 'linear', min: 0, padding: {bottom: 0},
			    		tick: { format: d3.format( "01d" ) },
	 					label: { text: '水分 / ナトリウム / カリウム', position: 'outer-middle' }
					}
				},
				point: { show: false },
				legend: { show: true, position: 'right' }
			});
		});

		pushBW();
		flashBW();
		dll = true;
		dl4 = true;
		dlf = true;
		displayBW();
	});
};

//				data: {
//					columns: [ minutes, d_energy, d_protein, d_fat, d_carbohydrate, d_fiber, d_sodium ],
//					x: 'minutes',
//					axes: {
//						#{l['data_bfr']}: 'y2',
//					},
//					labels: false,
//					type : 'line',
//					colors: {
//						#{l['data_weight']}: '#dc143c',
//						#{l['data_bfr']}: '#228b22'
//					},
//				},
//
//				axis: {
//			    	x: {
//			    		type: 'timeseries',
//			    		tick: { culling:true }
//					},
//					y: {
//			    		type: 'linear',
//						padding: {top: 100, bottom: 200 },
//						label: { text: '#{l['label_weight']}', position: 'outer-middle' }
//					}
//					y2: {
//						show: true,
//			    		type: 'linear',
//						padding: {top: 200, bottom: 100},
//	 					tick: { format: d3.format("01d") },
//	 					label: { text: '#{l['label_bfr']}', position: 'outer-middle' }
//					}
//				},
//
//				legend: { show: true, position: 'bottom' },
//
//				line: { connectNull: true, step: { type: 'step' }},
//				zoom: { enabled: true, type: 'drag' },
//			});
//
//	//--------------------------------------------------------------------------
//			var chart_sub = c3.generate({
//				bindto: '#visionnerz-blood',
//
//				data: {
//					columns: [
//						f_weight,
//						f_bfr,
//						r_weight,
//						r_bfr,
//						p_weight,
//						p_bfr,
//						rd_weight,
//						rd_bfr
//					],
//					xs: { #{l['data_first']}:'f_bfr', #{l['data_latest']}:'rd_bfr', #{l['data_recent']}:'p_bfr', #{l['data_past']}:'r_bfr' },
//					labels: true,
//					type : 'scatter',
//					colors: { #{l['data_first']}:'#4b0082', #{l['data_latest']}:'#dc143c', #{l['data_recent']}:'#00ff00', #{l['data_past']}:'#c0c0c0'}
//				},
//
//				axis: {
//			    	x: {
//						label: { text: '#{l['label_bfr']}', position: 'outer-center' },
//						padding: {left: 1, right: 1 },
//						tick: { fit: false }
//					},
//					y: {
//						label: { text: '#{l['label_weight']}', position: 'outer-middle' },
//						padding: {top: 20, bottom: 20 },
//						tick: { fit: false }
//					},
//				},
//				grid: {
//	     			x: { show: true },
//	        		y: { show: true }
//	            },
//				legend: { show: true, position: 'bottom' },
//				point: { show: true, r: 4 },
//				tooltip: { show: false }
//			});
//
//			var menergy = column[9];
//			document.getElementById( 'menergy' ).value = menergy;
//		});
//
//	};
//
//	drawChart();
//
//
//


/////////////////////////////////////////////////////////////////////////////////
// 3D recipe plott search //////////////////////////////////////////////////////////////

// Dosplaying recipe by scatter plott
const recipe3ds = function(){
	flashBW();
	$.post( "recipe3ds.cgi", { command:'plott_area' }, function( data ){
		$( "#L2" ).html( data );
		$.post( "recipe3ds.cgi", { command:'init' }, function( data ){
			$( "#L1" ).html( data );

			dl1 = true;
			dl2 = true;
			dl3 = true;
			displayBW();
		}).fail( function(){
			alert( "Error: Failed to load plotting area." );
		});
	});
};


/////////////////////////////////////////////////////////////////////////////////
// JSON edit //////////////////////////////////////////////////////////////

// JSON list init
var initJsonlist = function(){
	$.post( "jsonl.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};

/////////////////////////////////////////////////////////////////////////////////
// Media edit //////////////////////////////////////////////////////////////

// Media list init
const initMedialist = function(){
	$.post( "media-list.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Astral body projection //////////////////////////////////////////////////////////////

// Astral body init
var initAstral = function(){
	$.post( "astral.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};

// Astral body init
var changeAstral = function(){
	let astral_sw = 0;
	if( document.getElementById( "astral_sw" ).checked ){ astral_sw = 1; }

	$.post( "astral.cgi", { command:'change', astral_sw:astral_sw }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};


/////////////////////////////////////////////////////////////////////////////////
// Food flow //////////////////////////////////////////////////////////////

// Astral body init
var initFFlow = function(){
	$.post( "astral.cgi", { command:'init' }, function( data ){
		$( "#L1" ).html( data );

		flashBW();
		dl1 = true;
		displayBW();
	});
};
