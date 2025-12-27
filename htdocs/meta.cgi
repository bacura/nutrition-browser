#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser meta data viewer 0.0.2 (2025/06/18)

#==============================================================================
#STATIC
#==============================================================================
@debug = false
myself = File.basename( __FILE__ )

#==============================================================================
#LIBRARY
#==============================================================================
require './soul'

#==============================================================================
#DEFINITION
#==============================================================================

# Language pack
def language_pack( language )
	l = Hash.new

	#Japanese
	l['ja'] = {
		number: 		"登録数",
		account: 		"アカウント",
		total:			"累計",
		account_kind:	"アカウント種別",
		general:		"一般",
		admin_guest:	"管理用・ゲスト",
		guild_mem:		"ギルドメンバー",
		guild_mem_moe:	"ギルドメンバー・萌",
		guild_mem_shun:	"ギルドメンバー・旬",
		daughter:		"娘アカウント",
		food:			"食品",
		food_kind:		"食品種別",
		food_regular:	"正規食品",
		food_user:		"ユーザー食品",
		food_user_pub:	"公開ユーザー食品",
		recipe:			"レシピ",
		recipe_kind:	"レシピ種別",
		recipe_all:		"全レシピ",
		recipe_pub:		"全公開レシピ",
		recipe_san:		"さんレシピ",
		recipe_pub_san:	"さん公開レシピ",
		recipe_all_es:	"全レシピ（調味％を除く）",
		recipe_pub_es:	"全公開レシピ（調味％を除く）",
		menu:			"献立",
		menu_kind:		"献立種別",
		menu_all:		"全献立",
		menu_pub:		"公開献立"
	}

	return l[language]
end

def meta_section( title, data )
	<<-HTML
<h5>#{title}</h5>
<table class="table">
	<thead>
		<tr>
			<th scope="col" width='25%'>#{data[:kind_label]}</th>
			<th scope="col">#{data[:number_label]}</th>
		</tr>
	</thead>
	<tbody>
		#{data[:rows].map do |row| "<tr><td>#{row[:kind]}</td><td>#{row[:count]}</td></tr>" end.join}
	</tbody>
</table>
HTML
end

def meta_food( db, l )
	food_counts = {
		regular: db.query( "SELECT COUNT(*) AS count FROM #{$TB_FCT};", false ).first&.dig('count') || 0,
		user: db.query( "SELECT COUNT(*) AS count FROM #{$TB_FCTP} WHERE FN LIKE 'U%';", false ).first&.dig('count') || 0,
		public: db.query( "SELECT COUNT(*) AS count FROM #{$TB_FCTP} WHERE FN LIKE 'P%';", false ).first&.dig('count') || 0
	}

	meta_section(
		l[:food],
		kind_label: l[:food_kind],
		number_label: l[:number],
		rows: [
			{ kind: l[:food_regular], count: food_counts[:regular] },
			{ kind: l[:food_user], count: food_counts[:user] },
			{ kind: l[:food_user_pub], count: food_counts[:public] }
		]
	)
end

def meta_user( db, l )
	user_counts = {
		total: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER};", false ).first&.dig('count') || 0,
		general: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER} WHERE status=1;", false ).first&.dig('count') || 0,
		guild: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER} WHERE status=2;", false ).first&.dig('count') || 0,
		moe: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER} WHERE status=4;", false ).first&.dig('count') || 0,
		shun: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER} WHERE status=5;", false ).first&.dig('count') || 0,
		children: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER} WHERE status=6;", false ).first&.dig('count') || 0,
		admin: db.query( "SELECT COUNT(*) AS count FROM #{$TB_USER} WHERE status IN (3, 8, 9);", false ).first&.dig('count') || 0
	}

	meta_section(
		l[:account],
		kind_label: l[:account_kind],
		number_label: l[:number],
		rows: [
			{ kind: l[:total], count: user_counts[:total] },
			{ kind: l[:general], count: user_counts[:general] },
			{ kind: l[:guild_mem], count: user_counts[:guild] },
			{ kind: l[:guild_mem_moe], count: user_counts[:moe] },
			{ kind: l[:guild_mem_shun], count: user_counts[:shun] },
			{ kind: l[:admin_guest], count: user_counts[:admin] },
			{ kind: l[:daughter], count: user_counts[:children] }
		]
	)
end

def meta_recipe( db, l )
	recipe_counts = {
		total: db.query( "SELECT COUNT(*) AS count FROM #{$TB_RECIPE};", false ).first&.dig('count') || 0,
		real: db.query( "SELECT COUNT(*) AS count FROM #{$TB_RECIPE} WHERE role!=100;", false ).first&.dig('count') || 0,
		public: db.query( "SELECT COUNT(*) AS count FROM #{$TB_RECIPE} WHERE public=1;", false ).first&.dig('count') || 0,
		real_public: db.query( "SELECT COUNT(*) AS count FROM #{$TB_RECIPE} WHERE public=1 AND role!=100;", false ).first&.dig('count') || 0,
		user: db.query( "SELECT COUNT(*) AS count FROM #{$TB_RECIPE} WHERE user='#{db.user.name}';", false ).first&.dig('count') || 0,
		user_public: db.query( "SELECT COUNT(*) AS count FROM #{$TB_RECIPE} WHERE user='#{db.user.name}' AND public=1;", false ).first&.dig('count') || 0
	}

	meta_section(
		l[:recipe],
		kind_label: l[:recipe_kind],
		number_label: l[:number],
		rows: [
			{ kind: l[:recipe_all], count: recipe_counts[:total] },
			{ kind: l[:recipe_all_es], count: recipe_counts[:real] },
			{ kind: l[:recipe_pub], count: recipe_counts[:public] },
			{ kind: l[:recipe_pub_es], count: recipe_counts[:real_public] },
			{ kind: "#{db.user.name}#{l[:recipe_san]}", count: recipe_counts[:user] },
			{ kind: "#{db.user.name}#{l[:recipe_pub_san]}", count: recipe_counts[:user_public] }
		]
	)
end

def meta_menu( db, l )
	menu_counts = {
		total: db.query( "SELECT COUNT(*) AS count FROM #{$TB_MENU};", false ).first&.dig('count') || 0,
		public: db.query( "SELECT COUNT(*) AS count FROM #{$TB_MENU} WHERE public=1;", false ).first&.dig('count') || 0
	}

	meta_section(
		l[:menu],
		kind_label: l[:menu_kind],
		number_label: l[:number],
		rows: [
			{ kind: l[:menu_all], count: menu_counts[:total] },
			{ kind: l[:menu_pub], count: menu_counts[:public] }
		]
	)
end

#==============================================================================
# Main
#==============================================================================
html_init( nil )

user = User.new( @cgi )
l = language_pack( user.language )
db = Db.new( user, @debug, false )


#### Getting POST data
command = @cgi['command']
if @debug
	puts "command:#{command}<br>"
	puts "<hr>"
end

puts meta_user( db, l )
puts meta_food( db, l )
puts meta_recipe( db, l )
puts meta_menu( db, l )
