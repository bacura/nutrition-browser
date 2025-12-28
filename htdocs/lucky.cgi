#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser Lucky sum input driver 0.0.6 (2025/03/20)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'
require 'natto'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		lucky:	"Lucky☆",
		detect: "検出",
		food_no:	"食品番号",
		food:	"食品",
		memo:	"メモ",
		volume:	"量",
		unit:	"単位",
		adopt:	"採用",
		add:	"追　加"
	}

	return l[language]
end


def predict_html( lucky_data, db, l )
	html = ''

	# 仕上げ
	lucky_data.gsub!( /\n+/, "\n" )
	lucky_data.gsub!( /\t+/, '' )

	html << '<table class="table table-sm">'
	html << '<thead><tr>'
	html << "<th scope='col'>#{l[:detect]}</th>"
	html << "<th scope='col'>#{l[:food_no]}</th>"
	html << "<th scope='col'>#{l[:food]}</th>"
	html << "<th scope='col'>#{l[:memo]}</th>"
	html << "<th scope='col'>#{l[:volume]}</th>"
	html << "<th scope='col'>#{l[:unit]}</th>"
	html << "<th scope='col'>#{l[:adopt]}</th>"
	html << '</tr></thead>'

	id_counter = 0
	lucky_solid = lucky_data.split( "\n" )
	lucky_solid.delete( '' )

	lucky_solid.each do |e|
		food_no = ''
		weight = 100
		memo = ''
		vol = ''
		unit = ''
		food = e.split( '#' ).first
		food.gsub!( /\(/, '' )
		food.gsub!( /\)/, '' )
		puts food if @debug

		if food.size < 1
			puts "<br>" if @debug
			next 
		end
      	id_counter += 1

		puts 'vol~' if @debug
		vol_match = e.scan( /\#(.+)\#/ )
		unit_match = e.scan( /\[(.+)\]/ )

		vol = vol_match.size > 0 ? vol_match.first.first : ''
		unit = unit_match.size > 0 ? unit_match.first.first : 'g'
		food_no = vol.empty? ? '+' : food_no

		puts '<br>kakko~' if @debug
		memo_match = e.scan( /\((.+)\)/ )

		if memo_match.size > 0 && memo.empty?
			memo = memo_match.first.first
			food.gsub!( /\(.+\)/, '' )
		end

		puts '<br>Dic~' if @debug
		dic_hit = 0

		if memo == '' && food.size >= 1
			predict_food = ''
			r = db.query( "SELECT * FROM #{$TB_DIC} WHERE alias=?", false, [food] )
			dic_hit = r.size
			if r.first
				if r.first['def_fn'] != ''
					predict_food = r.first['org_name']
					food_no = r.first['def_fn']
					if food_no == nil
						res = db.query( "SELECT MIN(FN) FROM #{$TB_TAG} WHERE name=?", false, [predict_food] )&.first
						food_no = res['MIN(FN)']
					end
				else
					food_no = '+'
				end
			else
				food_sub_max = 0
				mecab = Natto::MeCab.new
				mecab.parse( food ) do |n|
					a = n.feature.force_encoding( 'utf-8' ).split( ',' )
		 			if a[0] == '名詞' && ( a[1] == '一般' || a[1] == '固有名詞' || a[1] == '普通名詞'  || a[1] == '人名' )
						if n.surface.size > food_sub_max
							rr = db.query( "SELECT * FROM #{$TB_DIC} WHERE alias=?", false, [n.surface] )
							if rr.first
								dic_hit = rr.size
								predict_food = rr.first['org_name']
								food_no = rr.first['def_fn']
								if food_no == nil
									rr = db.query( "SELECT MIN(FN) FROM #{$TB_TAG} WHERE name=?", false, [predict_food] )
									food_no = rr.first['MIN(FN)']
								end
								food_sub_max = n.surface.size
							end
						end
					end
				end

				food_no = '+' if predict_food == ''
			end
		end

		puts 'Unit~' if @debug
		if %w[+ '' nil].include?( food_no )
			food_no, predict_food, unit, dic_hit, vol, weight, memo = '+', '-', '-', '-', '-', '-', e.gsub( '#', '' ).gsub( '[', '' ).gsub( ']', '' )
		elsif vol.to_i == 0
			memo = unit
			unit, weight = 'g', 0
		else
			res = db.query( "SELECT unit FROM #{$TB_EXT} WHERE FN=?", false, [food_no] )&.first
			if res
				unith = JSON.parse( res['unit'] )
				weight = calculate_weight( unith, unit, vol )
			else
				memo = "#{vol}#{unit}"
				unit, vol, weight = 'g', 0, 0
			end
		end

		lucky_sum = "#{food_no}:#{weight}:#{unit}:#{vol}:0:#{memo}:1.0:#{weight}"

		puts 'Check~<br>' if @debug
		checked = food_no.empty? ? '' : 'CHECKED'
		disabled = food_no.empty? ? 'DISABLED' : ''

		html << '<tr>'
      	html << "<td>#{food}[#{dic_hit}]</td>"
      	html << "<td>#{food_no}</td>"
      	html << "<td>#{predict_food}</td>"
      	html << "<td>#{memo}</td>"
      	html << "<td>#{vol}</td>"
      	html << "<td>#{unit}</td>"
      	html << "<td><input type='checkbox' id='lucky#{id_counter}' #{checked} #{disabled}></td>"
      	html << "</tr>"
      	html << "<input type='hidden' id='lucky_sum#{id_counter}' value='#{lucky_sum}'></td>"

	end

	html << '</table><br>'

	html << '<div class="row" align="right">'
	html << "<button class='btn btn-sm btn-success' onclick=\"adoptLuckeyFood( '#{id_counter}' )\" >#{l[:add]}</button>"
	html << '</div>'

	return html
end

def calculate_weight( unith, unit, vol )
	if unith[ unit ]
		( vol.to_f * unith[ unit ].to_f ).round( 2 )
	elsif unith[ "#{unit}M" ]
		( vol.to_f * unith[ "#{unit}M" ].to_f ).round( 2 )
	elsif unith[ "#{unit}S" ]
		( vol.to_f * unith[ "#{unit}S" ].to_f ).round( 2 )
	elsif unith[ "#{unit}L" ]
		( vol.to_f * unith[ "#{unit}L" ].to_f ).round( 2 )
	else
		0
	end
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
user.debug if @debug
l = language_pack( user.language )
db = Db.new( user, @debug, false )


puts "POST<br>" if @debug
command = @cgi['command']
lucky_data = @cgi['lucky_data']
lucky_solid = @cgi['lucky_solid']
if @debug
	puts "command:#{command}<br>"
	puts "lucky_data:#{lucky_data}<br>"
	puts "lucky_solid:#{lucky_solid}<br>"
	puts "<hr>"
end


####
html = ''
case command
when 'init'

html = <<-"HTML"
<div class='container-fluid'>
	<div class='row'>
		<textarea class="form-control" rows="5" aria-label="lucky_data" id="lucky_data"></textarea>
	</div>
	<br>
	<div class='row'>
		<button type='button' class='btn btn-sm btn-info' onclick="analyzeLuckyFoods()">#{l[:lucky]}</button>
	</div>
</div>
HTML

# 解析
when 'analyze'
	candidate = nil

	# 特異データ検出
	# 栄養くん
	candidate = 'eiyo_kun' if /\[5A食品コード\]/ =~ lucky_data
	puts "candidate:#{candidate}<br>" if @debug

	case candidate
	when 'eiyo_kun'
		require "#{$HTDOCS_PATH}/lucky_/eiyo_kun.rb"
		html = ''
	else
		# 表記ゆれの統一
		lucky_data.tr!( '０-９ａ-ｚＡ-Ｚ','0-9a-zA-Z' )
		lucky_data.downcase!
		lucky_data.gsub!( "\r\n", "\n")
		lucky_data.gsub!( "\r", "\n")
		lucky_data.gsub!( /\n+/, "\n")

		lucky_data.gsub!( "\s", "\t")
		lucky_data.gsub!( "　", "\t")
		lucky_data.gsub!( ",", "\t")
		lucky_data.gsub!( /\t+/, "\t")
		lucky_data.gsub!( '．', '.')
		lucky_data.gsub!( '（', '(')
		lucky_data.gsub!( '）', ')')
		lucky_data.gsub!( '[', '')
		lucky_data.gsub!( ']', '')
		lucky_data.gsub!( '#', '')
		lucky_data.gsub!( '…', '')

		#瀕誤読表現
		lucky_data.gsub!( '玉ねぎ', "Dic-たまね" )
		lucky_data.gsub!( '玉葱', "Dic-たまね" )
		lucky_data.gsub!( 'オリーブオイル', "Dic-オリ油" )
		lucky_data.gsub!( 'オリーブ油', "Dic-オリ油" )
		lucky_data.gsub!( 'ゆず果汁', "Dic-ゆ汁" )
		lucky_data.gsub!( '柚子果汁', "Dic-ゆ汁" )

		# 単位の検出とマーク
		lucky_data.gsub!( /g/, "\t[g]" )
		lucky_data.gsub!( /ｇ/, "\t[g]" )
		lucky_data.gsub!( 'グラム', "\t[g]" )
		lucky_data.gsub!( /cup/, "\t[カップ]" )
		lucky_data.gsub!( 'カップ', "\t[カップ]" )
		lucky_data.gsub!( /ml/, "\t[ml]" )
		lucky_data.gsub!( 'cc', "\t[cc]" )
		lucky_data.gsub!( 'dl', "\t[dl]" )
		lucky_data.gsub!( 'cm', "\t[cm]" )
		lucky_data.gsub!( '大さじ', "\t[大さじ]" )
		lucky_data.gsub!( '大匙', "\t[大さじ]" )
		lucky_data.gsub!( 'おおさじ', "\t[大さじ]" )
		lucky_data.gsub!( '小さじ', "\t[小さじ]" )
		lucky_data.gsub!( '小匙', "\t[小さじ]" )
		lucky_data.gsub!( 'こさじ', "\t[小さじ]" )

		lucky_data.gsub!( '本', "\t[本]" )
		lucky_data.gsub!( '枚', "\t[枚]" )
		lucky_data.gsub!( '個', "\t[個]" )
		lucky_data.gsub!( '玉', "\t[玉]" )
		lucky_data.gsub!( '株', "\t[株]" )
		lucky_data.gsub!( '匹', "\t[匹]" )
		lucky_data.gsub!( '切れ', "\t[切れ]" )
		lucky_data.gsub!( '片', "\t[片]" )
		lucky_data.gsub!( '束', "\t[束]" )
		lucky_data.gsub!( '缶', "\t[缶]" )

		lucky_data.gsub!( 'ひとつまみ', "\t1\t[つまみ]" )
		lucky_data.gsub!( 'ふたつまみ', "\t2\t[つまみ]" )
		lucky_data.gsub!( '半分', "\t0.5\t[個]" )

		lucky_data.gsub!( '適量', "\t0\t[適量]" )
		lucky_data.gsub!( '適当', "\t0\t[適当]" )
		lucky_data.gsub!( '少々', "\t0\t[少々]" )
		lucky_data.gsub!( 'お好み', "\t0\t[お好み]" )
		lucky_data.gsub!( '好み', "\t0\t[お好み]" )

		# 分数の処理
		lucky_data = lucky_data.gsub( /(\d+)\/(\d+)/ ) do |x|
			x = ( $1.to_f / $2.to_f ).round( 2 ).to_s
		end

		# 数値→単位の順番に並べ替える
		lucky_data = lucky_data.gsub( /(\[[^\[]+\])\t?(\d+\.?\d*)/ ) do |x|
			x = "#{$2}\t#{$1}"
		end

		# 単位の後で改行
		lucky_data = lucky_data.gsub( /(\[[^\[]+\])/ ) do |x|
			x = "#{$1}\n"
		end

		# ()付き数字のマーク
		lucky_data = lucky_data.gsub( /(\(\d+g\))/ ) do |x|
			x = ""
		end

		# 範囲の平均化
		lucky_data = lucky_data.gsub( /(\d+)\-(\d+)/ ) do |x|
			ave = ( $1.to_f + $2.to_f ) / 2
			x = ave
		end

		# 数字のマーク
		lucky_data = lucky_data.gsub( /(\d+\/?\.?\d*)/ ) do |x|
			x = "##{$1}#"
		end
	end


	html = predict_html( lucky_data, db, l )

when 'push'
	puts "Push<br>" if @debug
	new_sum = ''
	lucky_solid.sub!( /^\t/, '' )

	# まな板データの読み込み
	res = db.query( "SELECT sum from #{$TB_SUM} WHERE user=?", false, [user.name] )&.first
	new_sum << res['sum'] if res
	new_sum << "\t" if new_sum != ''
	new_sum << lucky_solid if lucky_solid != ''

	# まな板データ更新
	db.query( "UPDATE #{$TB_SUM} SET sum=? WHERE user=?", true, [new_sum, user.name] )
else
	puts 'Default<br>' if @debug
	html = 'lucky driver error'
end

puts html

#==============================================================================
# FRONT SCRIPT
#==============================================================================
if command == 'init'
js = <<-"JS"
<script type='text/javascript'>

var postReqLuck = ( command, data, successCallback ) => {
	$.post( '#{myself}', { command, ...data })
		.done( successCallback )
		.fail(( jqXHR, textStatus, errorThrown ) => {
			console.error( "Request failed: ", textStatus, errorThrown );
			alert( "An error occurred. Please try again." );
		});
};

var analyzeLuckyFoods = () => {
	var lucky_data = $( '#lucky_data' ).val();
	if( lucky_data != '' ){
		postReqLuck( 'analyze', { lucky_data }, data => {
			$( "#L2" ).html( data );
			displayVIDEO( 'Lucky?' );
		});
	}
};

var adoptLuckeyFood = ( idc ) => {
	let lucky_solid = '';
	for (let i = 1; i <= idc; i++) {
	    let $lucky = $("#lucky" + i);
	    let $lucky_sum = $("#lucky_sum" + i);

	    if ($lucky.is(":checked") && $lucky_sum.val() !== '') {
	        lucky_solid += $lucky_sum.val() + "\t";
	    }
	}

	if( lucky_solid != '' ){
		postReqLuck( 'push', { lucky_solid }, data => {
			$( "#L2" ).html( data );
			displayVIDEO( 'Lucky?' );

			initCB( 'refresh', '', null )
		});
	}
};
</script>
JS

puts js

end
