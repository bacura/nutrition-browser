# Nutorition browser 2020 Config module for code converter 0.11b (2023/07/13)
#encoding: utf-8

@debug = false

####
def confirm_result_html( target, from, into, ignore_p, count, l )
	cb = ''
	cb = "<button type='button' class='btn btn-warning btn-sm' onclick=\"convert_#{target}2( 'exchange-#{target}', '#{from}', '#{into}', '#{ignore_p}' )\">#{l['convert']}</button>" if count > 0
	ignore = l['protect-off']
	ignore = l['protect-on'] if ignore_p == 'on'
	into_view = into
	into_view = l['delete'] if into == ''

	####
####
html = <<-"HTML_CR"
<div class="container">
	<div class="row">
		<div class='col-4'>#{from}&nbsp;&nbsp;#{l['arrow-r']}&nbsp;&nbsp;#{into_view}</div>
		<div class='col-2'>[#{ignore}]</div>
		<div class='col-2'>#{count} #{l['hit-r']}</div>
	</div>
	<br>
	<div class="row">
	#{cb}
</div>
HTML_CR
####
	####

	return html
end


####
def exchange_result_html( count, l )
	####
####
html = <<-"HTML_ER"
<div class="container">
	<div class="row">
		<div class='col-2'>#{count} #{l['result']}</div>
	</div>
</div>
HTML_ER
####
	####

	return html
end


def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )

	from_fn = cgi['from_fn'].to_s
	into_fn = cgi['into_fn'].to_s
	ignore_p = cgi['ignore_p']
	from_tag = cgi['from_tag'].to_s
	into_tag = cgi['into_tag'].to_s
	ignore_tagp = cgi['ignore_tagp']

	html = ''
	case cgi['step']
	when 'confirm-fn'
		r = db.query( "SELECT * FROM #{$TB_TAG} WHERE FN='#{into_fn}';", false )
		if r.first
			rr = db.query( "SELECT * FROM #{$TB_TAG} WHERE FN='#{from_fn}';", false )
			if rr.first
				count = 0
				protect = ''
				protect = ' AND protect!="1"' if ignore_p == 'off'
				rrr = db.query( "SELECT sum FROM #{$TB_RECIPE} WHERE user='#{db.user.name}'#{protect};", false )
				rrr.each do |e|
					hit_flag = false
					a = e['sum'].split( "\t" )
					a.each do |ee|
						sum = ee.split( ':' )
						hit_flag = true if from_fn == sum[0]
					end
					count += 1 if hit_flag
				end

				#
				html << confirm_result_html( 'fn', rr.first['name'], r.first['name'], ignore_p, count, l )

			else
				html << "#{l['no_fn1']}"
			end
		else
			html << "#{l['no_fn2']}"
		end

	when 'exchange-fn'
		count = 0
		protect = ''
		protect = ' AND protect!="1"' if ignore_p == 'off'
		r = db.query( "SELECT sum, code, user FROM #{$TB_RECIPE} WHERE user='#{db.user.name}'#{protect};", false )
		r.each do |e|
			sums = []
			a = e['sum'].split( "\t" )
			a.each do |ee|
				aa = ee.split( ':' )
				if aa[0] == from_fn
					aa[2] = 'g'
					aa[3] = a[1]
					aa[6] = 1.0
					aa[7] = a[1]
					sums << aa.join( ':' )
				else
					sums << ee
				end
			end
			sum_post = sums.join( "\t" )

			if e['sum'] != sum_post
				db.query( "UPDATE #{$TB_RECIPE} set sum='#{sum_post}' WHERE user='#{db.user.name}' AND code='#{e['code']}';", true )
				count += 1
			end
		end

    	html << exchange_result_html( count, l )

	when 'confirm-tag'
		count = 0
		protect = ''
		protect = ' AND protect!="1"' if ignore_tagp == 'off'

		r = db.query( "SELECT code, protocol FROM #{$TB_RECIPE} WHERE user='#{db.user.name}'#{protect};", false )
		r.each do |e|
			a = e['protocol'].split( "\n" )
			if /^\#/ =~ a[0]
				count += 1 if a[0].match?( from_tag )
			end
		end

		html << confirm_result_html( 'tag', from_tag, into_tag, ignore_p, count, l )

	when 'exchange-tag'
		count = 0
		protect = ''
		protect = ' AND protect!="1"' if ignore_p == 'off'

		recipe = Recipe.new( user.name )
		r = db.query( "SELECT code, protocol FROM #{$TB_RECIPE} WHERE user='#{db.user.name}'#{protect};", false )
		r.each do |e|
			recipe.load_db( e['code'], true )
			a = recipe.protocol.split( "\n" )
			if /^\#/ =~ a[0]
				if a[0].match?( from_tag )
					a[0].gsub!( "　", "\s" )
					a[0].gsub!( from_tag, into_tag )
					a[0].gsub!( "\s\s", "\s" )
					recipe.protocol = a.join( "\n" )
					recipe.update_db
					count += 1
				end
			end
		end

    	html << exchange_result_html( count, l )
	else

		####
########
html = <<-"HTML"
<div class="container">
	<div class='row'>
    	<div class='col-2'>#{l['fn']}</div>
    	<div class='col-6'>
    		<div class='input-group'>
	    		<input type="text" id="from_fn" class="form-control form-control-sm" placeholder='#{l['food1']}'>
	    		&nbsp;&nbsp;#{l['arrow-r']}&nbsp;&nbsp;
				<input type="text" id="into_fn" class="form-control form-control-sm" placeholder='#{l['food2']}'>
			</div>
		</div>
    	<div class='col-2'>
    		<div class="form-check">
				<input class="form-check-input" type="checkbox" value="on" id="ignore_p">
				<label class="form-check-label">#{l['protect-on']}</label>
			</div>
		</div>
		<div class='col' align="right"><button type="button" class="btn btn-outline-primary btn-sm nav_button" onclick="convert_fn( 'confirm-fn' )">#{l['confirm']}</button></div>
	</div>
	<hr>

	<div class='row'>
    	<div class='col-2'>#{l['tag']}</div>
    	<div class='col-6'>
    		<div class='input-group'>
	    		<input type="text" id="from_tag" class="form-control form-control-sm" placeholder='#{l['tag1']}'>
	    		&nbsp;&nbsp;#{l['arrow-r']}&nbsp;&nbsp;
				<input type="text" id="into_tag" class="form-control form-control-sm" placeholder='#{l['tag2']}'>
			</div>
		</div>
    	<div class='col-2'>
    		<div class="form-check">
				<input class="form-check-input" type="checkbox" value="on" id="ignore_tagp">
				<label class="form-check-label">#{l['protect-on']}</label>
			</div>
		</div>
		<div class='col' align="right"><button type="button" class="btn btn-outline-primary btn-sm nav_button" onclick="convert_tag( 'confirm-tag' )">#{l['confirm']}</button></div>
	</div>
</div>
HTML
########
		####
	end

	return html
end


def module_js()
	js = <<-"JS"
<script type='text/javascript'>

// Food number converter init
var convert_fn = function( step ){
	const from_fn = document.getElementById( "from_fn" ).value;
	const into_fn = document.getElementById( "into_fn" ).value;
	let ignore_p = 'off';

	if( document.getElementById( "ignore_p" ).checked ){ ignore_p = 'on'; }
	if( from_fn != '' && into_fn != '' ){
		if( into_fn != from_fn ){
			$.post( "config.cgi", { mod:'convert', step:step, from_fn:from_fn, into_fn:into_fn, ignore_p:ignore_p }, function( data ){
				$( "#L2" ).html( data );

				flashBW();
				dl1 = true;
				dl2 = true;
				dline = true;
				displayBW();
			});
		}else{
			displayVIDEO( 'Same!(>_<)');
		}
	}else{
		displayVIDEO( 'Empty!(>_<)');
	}
};

// Recipe tag converter init
var convert_tag = function( step ){
	const from_tag = document.getElementById( "from_tag" ).value;
	const into_tag = document.getElementById( "into_tag" ).value;
	let ignore_tagp = 'off';

	if( document.getElementById( "ignore_tagp" ).checked ){ ignore_tagp = 'on'; }
	if( into_fn != from_tag && from_tag != '' ){
		$.post( "config.cgi", { mod:'convert', step:step, from_tag:from_tag, into_tag:into_tag, ignore_tagp:ignore_tagp }, function( data ){
			$( "#L2" ).html( data );

			flashBW();
			dl1 = true;
			dl2 = true;
			dline = true;
			displayBW();
		});
	}else{
		displayVIDEO( 'Same!(>_<)');
	}
};


// Food number converter exchange
var convert_fn2 = function( step, from_fn, into_fn, ignore_p ){
	$.post( "config.cgi", { mod:'convert', step:step, from_fn:from_fn, into_fn:into_fn, ignore_p:ignore_p }, function( data ){ $( "#L2" ).html( data );});
};

// Recipe tag converter exchange
var convert_tag2 = function( step, from_tag, into_tag, ignore_tagp ){
	$.post( "config.cgi", { mod:'convert', step:step, from_tag:from_tag, into_tag:into_tag, ignore_tagp:ignore_tagp }, function( data ){ $( "#L2" ).html( data );});
};

</script>
JS
	puts js
end


# Langege pack
def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "食品番号・タグ変換",\
		'fn' => "レシピ［食品番号］",\
		'tag' => "レシピ［タグ］",\
		'food1' => "元食品番号",\
		'arrow-r' => "＞＞",\
		'food2' => "先食品番号",\
		'confirm' => "確認",\
		'no_fn1' => "変換元の食品番号は存在しません。",\
		'no_fn2' => "変換先の食品番号は存在しません。",\
		'protect-on' => "保護レシピを含める",\
		'protect-off' => "保護レシピを除外する",\
		'hit-r' => "レシピが該当します",\
		'convert' => "変　換",\
		'delete' => "[消去]",\
		'result' => "レシピを変換しました",\
		'tag1' => "元タグ",\
		'tag2' => "先タグ"
	}

	return l[language]
end
