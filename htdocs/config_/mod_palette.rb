# Nutorition browser 2020 Config module for Palette 0.2.1 (2025/12/27)
#encoding: utf-8

@degug = false

#### displying palette
def listing( db, l )
	r = db.query( "SELECT * FROM #{$TB_PALETTE} WHERE user=?", false, [db.user.name] )
	list_body = ''
	r.each do |e|
		count = e['palette'].count( '1' )
		list_body << "<tr><td>#{e['name']}</td><td>#{count}</td>"
		list_body << "<td><button class='btn btn-outline-primary btn-sm' type='button' onclick='palette_cfg( \"edit_palette\", \"#{e['name']}\" )'>#{l[:edit]}</button></td>"
		list_body << "<td>"
		list_body << "<input type='checkbox' id=\"#{e['name']}\">&nbsp;<button class='btn btn-outline-danger btn-sm' type='button' onclick='palette_cfg( \"delete_palette\", \"#{e['name']}\" )'>#{l[:delete]}</button></td></tr>\n" unless e['name'] == '簡易表示用'
		list_body << "</td></tr>"
	end


	html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<div class='col-8'><h5>#{l[:palette_list]}</h5></div>
		<div class='col-2'><button class="btn btn-outline-primary btn-sm" type="button" onclick="palette_cfg( 'new_palette', '' )">#{l[:new_palette]}</button></div>
		<div class='col-2'><button class="btn btn-outline-danger btn-sm" type="button" onclick="palette_cfg( 'reset_palette', '' )">#{l[:reset]}</button></div>
	</div>
	<br>

	<table class="table table-sm table-hover">
	<thead>
		<tr>
			<td>#{l[:palette_name]}</td>
			<td>#{l[:fc_num]}</td>
			<td>#{l[:operation]}</td>
			<td></td>
		</tr>
	</thead>
	#{list_body}

	</table>
</div>
HTML

	return html
end


def config_module( cgi, db )
	module_js()
	l = module_lp( db.user.language )

	step = cgi['step']
	html = ''

	case step
	when ''
		html = listing( db, l )

	when 'new_palette', 'edit_palette'
		checked = Hash.new
		if step == 'edit_palette'
			res = db.query( "SELECT * FROM #{$TB_PALETTE} WHERE user=? AND name=?", false, [db.user.name, cgi['palette_name']] )&.first
			if res
				palette = res['palette']
				palette.size.times do |c|
					checked[@fct_item[c]] = 'checked' if palette[c] == '1'
				end
			end
		end

		fc_table = ['', '', '', '', '', '', '']
		@fct_rew.each do |e| fc_table[0] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end
		@fct_pf.each do |e| fc_table[1] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end
		@fct_cho.each do |e| fc_table[2] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end
		@fct_m.each do |e| fc_table[3] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end
		@fct_fsv.each do |e| fc_table[4] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end
		@fct_wsv.each do |e| fc_table[5] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end
		fc_table[5] << "<tr><td><hr></td></tr>"
		@fct_as.each do |e| fc_table[5] << "<tr><td><input type='checkbox' id='#{e}' #{checked[e]}>&nbsp;#{@fct_name[e]}</td></tr>" end

		html = <<-"HTML"
	<div class="container-fluid">
		<div class="row">
			<div class="col-6">
				<div class="input-group mb-3">
  					<span class="input-group-text">#{l[:palette_name]}</span>
  					<input type="text" class="form-control" id="palette_name" value="#{cgi['palette_name']}" maxlength="60">
  				</div>
			</div>
			<div class="col-5"></div>
			<div class="col-1"><button class="btn btn-outline-primary btn-sm" type="button" onclick="palette_cfg( 'regist' )">#{l[:regist]}</button></div>
		</div>
		<br>
		<div class="row">
			<div class="col-4"><table class='table-sm table-striped' width='100%'>#{fc_table[0]}</table></div>
			<div class="col-4"><table class='table-sm table-striped' width='100%'>#{fc_table[1]}</table></div>
			<div class="col-4"><table class='table-sm table-striped' width='100%'>#{fc_table[2]}</table></div>
		<div class="row">
		<hr>
		</div>
			<div class="col-4"><table class='table-sm table-striped' width='100%'>#{fc_table[3]}</table></div>
			<div class="col-4"><table class='table-sm table-striped' width='100%'>#{fc_table[4]}</table></div>
			<div class="col-4"><table class='table-sm table-striped' width='100%'>#{fc_table[5]}</table></div>
		</div>
	</div>
HTML

	when 'regist'
		fct_bits = '0000'
		palette_name = cgi['palette_name']

		@fct_min.each do |e| fct_bits << cgi[e].to_i.to_s end
		res = db.query( "SELECT * FROM #{$TB_PALETTE} WHERE name=? AND user=?", false, [palette_name, db.user.name] )&.first
		if res
			db.query( "UPDATE #{$TB_PALETTE} SET palette=? WHERE name=? AND user=?", true, [fct_bits, palette_name, db.user.name] )
		else
			db.query( "INSERT INTO #{$TB_PALETTE} SET palette=?, name=?, user=?", true, [fct_bits, palette_name, db.user.name] )
		end

		html = listing( db, l )

	when 'delete_palette'
		db.query( "DELETE FROM #{$TB_PALETTE} WHERE name=? AND user=?", true, [cgi['palette_name'], db.user.name] )

		html = listing( db, l )

	when 'reset_palette'
		db.query( "DELETE FROM #{$TB_PALETTE} WHERE user=?", true, [db.user.name] )
		0.upto( @palette_default.size - 1 ) do |c|
			db.query( "INSERT INTO #{$TB_PALETTE} SET user=?, name=?, palette=?", true, [db.user.name, @palette_default_name[c], @palette_default[c]] )
		end
		html = listing( db, l )
	end

	return html
end


def module_js()
	js_fc_set = ''
	post_fc_set = ''

	@fct_min.each do |e|
		js_fc_set << "if( document.getElementById( '#{e}' ).checked ){ var #{e} = 1 }"
		post_fc_set << "#{e},"
	end
	post_fc_set.chop!

	js = <<-"JS"
<script type='text/javascript'>

// Sending FC palette
var palette_cfg = ( step, id ) => {

	flashBW();
	if( step == 'new_palette' ){
		postLayer( 'config.cgi', 'dummy', true, 'L2', { mod:'palette', step });

		dl2 = true;
		displayBW();
	}

	if( step == 'reset_palette' ){
		postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'palette', step });

		displayVIDEO( 'Reset' );
	}

	if( step == 'regist' ){
		const palette_name = document.getElementById( "palette_name" ).value;

		if( palette_name != '' ){
			#{js_fc_set}

			postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'palette', step, palette_name, #{post_fc_set} });

			displayVIDEO( palette_name );

		}else{
			displayVIDEO( 'Palette name!(>_<)' );
		}
	}

	// Edit FC palette
	if( step == 'edit_palette' ){
		postLayer( 'config.cgi', 'dummy', true, 'L2', { mod:'palette', step, palette_name:id });

		dl2 = true;
		displayBW();
	}

	// Deleting FC palette
	if( step == 'delete_palette' ){
		if( document.getElementById( id ).checked ){
			postLayer( 'config.cgi', 'dummy', true, 'L1', { mod:'palette', step, palette_name:id });

		}else{
			displayVIDEO( 'Check!(>_<)' );
		}
	}
	dl1 = true;
	dline = true;
	displayBW();

};

</script>
JS
	puts js
end


def module_lp( language )
	l = Hash.new
	l['ja'] = {
		'mod_name' => "成分パレット",
		mod_name:	"成分パレット",
		edit:	"編集",
		delete: "削除",
		palette_list:	"カスタム成分パレット一覧",
		new_palette:	"新規登録",
		reset:	"リセット",
		palette_name:	"パレット名",
		fc_num:	"成分数",
		operation:	"操作",
		regist:	"登録"
	}

	return l[language]
end
