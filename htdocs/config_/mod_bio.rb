# Nutorition browser 2020 Config module for bio 0.3.0 (2025/12/27)
#encoding: utf-8

@debug = false

def config_module( cgi, db )
	module_js( cgi['mod'] )
	l = module_lp( db.user.language )
	time_set = [5, 10, 15, 20, 30, 45, 60, 90, 120]

	step = cgi['step']

	res = db.query( "SELECT bio FROM #{$TB_CFG} WHERE user=?", false, [db.user.name] )&.first
	unless res['bio'].to_s.empty?

		begin
			bio = JSON.parse( res['bio'] )
		rescue JSON::ParserError => e
			puts "J(x_x)pE: #{e.message}<br>"
			exit
		end     

		sex = bio['sex'].to_i
		age = bio['age'].to_i
		birth = bio['birth']
		height = bio['height'].to_f
		weight = bio['weight'].to_f
		kexow = bio['kexow'].to_i
		pgene = bio['pgene'].to_i

		bst = bio['bst']
		lst = bio['lst']
		dst = bio['dst']
		bti = bio['bti'].to_i
		lti = bio['lti'].to_i
		dti = bio['dti'].to_i
	end

	if step ==  'change'
		sex = cgi['sex'].to_i
		age = cgi['age'].to_i
		birth = cgi['birth']
		height = cgi['height'].to_f
		weight = cgi['weight'].to_f
		kexow = cgi['kexow'].to_i
		pgene = cgi['pgene'].to_i

		bst = cgi['bst']
		lst = cgi['lst']
		dst = cgi['dst']
		bti = cgi['bti'].to_i
		lti = cgi['lti'].to_i
		dti = cgi['dti'].to_i

		# Updating bio information
		bio_ = JSON.generate( { "sex" => sex, "age" => age, "birth" => birth, "height" => height, "weight" => weight, "kexow" => kexow, "pgene" => pgene, "bst" => bst, "lst" => lst , "dst" => dst, "bti" => bti , "lti" => lti , "dti" => dti } )
		db.query( "UPDATE #{$TB_CFG} SET bio=? WHERE user=?", true, [bio_, db.user.name] )
	end

	photo = Media.new( db.user )
	if step == 'photo_upload'
		photo.load_cgi( cgi )
    	photo.get_series()
		photo.delete_series( true )
		photo.save_photo( cgi )
    	photo.save_db()
	end

	if step == 'photo_del'
		photo.load_cgi( cgi )
		photo.delete_photo( true )
		photo.delete_db( true )
	end

	photo.base = 'bio'
	photo.origin = db.user.name
	photo_code = photo.get_series().first
	unless photo_code.to_s.empty?
		profile_photo = "<img src='photo.cgi?iso=Q&code=#{photo_code}&tn=-tn' width='120px' class='img-thumbnail'>"
		photo_trash = "<span onclick=\"photoDel( '#{photo_code}' )\">#{l[:trash]}</span>"
	else
		profile_photo = "<img src='#{$PHOTO}/nobody.jpg' width='100px' class='img-thumbnail'>"
		photo_trash = ''
	end

	if sex == 0
		male_check = 'CHECKED'
		female_check = ''
	else
		male_check = ''
		female_check = 'CHECKED'
	end

	if db.user.status >= 2
		kexow_check = 'CHECKED' if kexow == 1
	else
		kexow_check = ''
		kexow_disabled = 'DISABLED'
	end

	if db.user.status >= 2
		pgene_check = 'CHECKED' if pgene == 1
	else
		pgene_check = ''
		pgene_disabled = 'DISABLED'
	end

  	bti_select = "<select class='form-select' id='bti'>"
	time_set.each do |e| bti_select << "<option value='#{e}' #{$SELECT[e == bti]}>#{e}</option>" end
  	bti_select << "</select>"

  	lti_select = "<select class='form-select' id='lti'>"
	time_set.each do |e| lti_select << "<option value='#{e}' #{$SELECT[e == lti]}>#{e}</option>" end
  	lti_select << "</select>"

  	dti_select = "<select class='form-select' id='dti'>"
	time_set.each do |e| dti_select << "<option value='#{e}' #{$SELECT[e == dti]}>#{e}</option>" end
  	dti_select << "</select>"

	html = <<~"HTML"
    <div class="container">
    	<div class='row'>
			<div class='col-6'>
		    	<div class='row'>
			    	<div class='col-4'>#{l[:sex]}</div>
					<div class='col-8'>
						<div class='form-check form-check-inline'>
							<input class='form-check-input' type='radio' name='sex' id='male' #{male_check}>
							<label class='form-check-label'>#{l[:male]}</label>
						</div>
						<div class='form-check form-check-inline'>
							<input class='form-check-input' type='radio' name='sex' id='female' #{female_check}>
							<label class='form-check-label'	>#{l[:female]}</label>
						</div>
					</div>
				</div>
				<br>

		    	<div class='row'>
			    	<div class='col-4'>#{l[:birth]}</div>
					<div class='col-6'><input type="date" id='birth' class="form-control login_input" value="#{birth}"></div>
				</div>

		    	<div class='row'>
			    	<div class='col-4'>#{l[:height]}</div>
					<div class='col-6'><input type="text" maxlength="5" id="height" class="form-control login_input" value="#{height}"></div>
				</div>

		    	<div class='row'>
			    	<div class='col-4'>#{l[:weight]}</div>
					<div class='col-6'><input type="text" maxlength="5" id="weight" class="form-control login_input" value="#{weight}"></div>
				</div>
			</div>
			<div class='col-6'>

		    	<div class='row'>
					<div class='col-8'>
						<form method='post' enctype='multipart/form-data' id='bio_puf'>
							<div class="input-group input-group-sm">
								<label class='input-group-text' for='photo' >#{l[:camera]}</label>
								<input type='file' class='form-control' id='photo' name='photo' onchange="PhotoUpload( '#{db.user.name}' )">
							</div>
						</form>
					</div>
				</div>
				<br>

		    	<div class='row'>
					<div class='col'>
					#{profile_photo}&nbsp;&nbsp;
		    		#{photo_trash}

				</div>
				</div>

			</div>
		</div>
		<hr>

    	<div class='row'>
	    	<div class='col-2'></div>
			<div class='col-4'>
				<div class="form-check">
					<input class="form-check-input" type="checkbox" id="kexow" #{kexow_check} #{kexow_disabled}>#{l[:kexow]}
				</div>
			</div>
		</div>
    	<div class='row'>
	    	<div class='col-2'></div>
			<div class='col-4'>
				<div class="form-check">
					<input class="form-check-input" type="checkbox" id="pgene" #{pgene_check} #{pgene_disabled}>#{l[:pgene]}
				</div>
			</div>
		</div>
		<hr>

    	<div class='row'>
	    	<div class='col-2'>#{l[:bst]}</div>
			<div class='col-4'>
				<div class='input-group input-group-sm'>
					<input type='time' class='form-control' id='bst' value='#{bst}'>
					<span class='input-group-text'>#{l[:meal_start]}</span>
					#{bti_select}
					<span class='input-group-text'>#{l[:meal_time]}</span>
				</div>
			</div>
		</div>
		<br>

    	<div class='row'>
	    	<div class='col-2'>#{l[:lst]}</div>
			<div class='col-4'>
				<div class='input-group input-group-sm'>
					<input type='time' class='form-control' id='lst' value='#{lst}'>
					<span class='input-group-text'>#{l[:meal_start]}</span>
					#{lti_select}
					<span class='input-group-text'>#{l[:meal_time]}</span>
				</div>
			</div>
		</div>
		<br>

    	<div class='row'>
	    	<div class='col-2'>#{l[:dst]}</div>
			<div class='col-4'>
				<div class='input-group input-group-sm'>
					<input type='time' class='form-control' id='dst' value='#{dst}'>
					<span class='input-group-text'>#{l[:meal_start]}</span>
					#{dti_select}
					<span class='input-group-text'>#{l[:meal_time]}</span>
				</div>
			</div>
		</div>
		<hr>

    	<div class='row'>
	    	<div class='col-2'></div>
			<div class='col-4'><button type="button" class="btn btn-outline-primary btn-sm nav_button" onclick="bio_cfg( 'change' )">#{l[:save]}</button></div>
		</div>
	</div>
HTML
	return html
end


def module_js( mod )
	js = <<-"JS"
<script type='text/javascript'>

// Updating bio information
var bio_cfg = function( step ){
	let age = '';
	let height = '';
	let weight = '';
	let bst = '07:00';
	let lst = '12:00';
	let dst = '19:00';
	let bti = 15;
	let lti = 15;
	let dti = 15;
	let sex = 0;
	let kexow = 0;
	let pgene = 0;

	if( step == 'change' ){
		birth = document.getElementById( "birth" ).value;
		height = document.getElementById( "height" ).value;
		weight = document.getElementById( "weight" ).value;
		bst = document.getElementById( "bst" ).value;
		lst = document.getElementById( "lst" ).value;
		dst = document.getElementById( "dst" ).value;
		bti = document.getElementById( "bti" ).value;
		lti = document.getElementById( "lti" ).value;
		dti = document.getElementById( "dti" ).value;
		if( document.getElementById( "female" ).checked ){ sex = 1; }
		if( document.getElementById( "kexow" ).checked ){ kexow = 1; }
		if( document.getElementById( "pgene" ).checked ){ pgene = 1; }
	}
	postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'#{mod}', step, sex, age, birth, height, weight, kexow, pgene, bst, lst, dst, bti, lti, dti });

	flashBW();
	dl1 = true;
	dline = true;
	displayBW();
};


var PhotoUpload = ( uname ) => {
	const formData = new FormData( $( '#bio_puf' )[0] );
	formData.append( 'mod', '#{mod}' );
	formData.append( 'step', 'photo_upload' );
	formData.append( 'origin', uname );
	formData.append( 'base', 'bio' );
	formData.append( 'alt', 'profile_image' );
	formData.append( 'secure', '1' );

	$.ajax( {
		url: "config.cgi",
		type: 'POST',
		processData: false,
		contentType: false,
		data: formData,
		dataType: 'html',
		success: ( data ) => $( '#L1' ).html( data )
	} );
}


var photoDel = ( code ) => {
	postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'#{mod}', step:'photo_del', code, base:'bio', secure:1 });
}

</script>
JS
	puts js
end


def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "生体情報",
		sex: "代謝的性別",
		male: "男性",
		female: "女性",
		age: "年齢（廃止予定）",
		height: "身長(m)",
		weight: "体重(kg)",
		kexow: "拡張こよみ上書き",
		save: "保存",
		birth: "生年月日",
		pgene: "ぽっちゃり（倹約）遺伝子が働いている気がする",
		bst: "朝食",
		lst: "昼食",
		dst: "夕食",
		meal_time: "分間",
		meal_start: "開始",
		trash: "<img src='bootstrap-dist/icons/trash-fill.svg' style='height:2em; width:2em;'>",
		camera: "<img src='bootstrap-dist/icons/camera.svg' style='height:1.2em; width:1.2em;'>"
	}

	return l[language]
end
