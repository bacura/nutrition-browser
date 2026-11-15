#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 export 0.2.0 (2026/11/07)

ENV['REQUEST_METHOD'] = 'GET'
ENV['GATEWAY_INTERFACE'] = 'CGI/1.1'
#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'
require 'date'
require 'time'

#==============================================================================
#STATIC
#==============================================================================
@debug = false

#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================

case ARGV[0]
when 'unit'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['unit']}\n" end
	puts "NB2020 [unit] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'gycv'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT} WHERE gycv=1;" )
	r.each do |e| export << "#{e['FN']}\n" end
	puts "NB2020 [gycv] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'shun'
	export = ''
	r = $DB.query( "SELECT FN, LPAD( BIN( shun ), 12, '0' ) AS shun_bit FROM #{$TB_EXT};" )
	r.each do |e|
		export << "#{e['FN']}\t#{e['shun_bit']}\n" unless /[PCU]/ =~ e['FN'] || e['FN'].empty?
	end
	puts "NB2020 [shun] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'allergen'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT};" )
	r.each do |e| export << "#{e['FN']}\t#{e['allergen1']}\t#{e['allergen2']}\n" end
	puts "NB2020 [allergen] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'dic'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_DIC} ORDER BY FG, org_name;" )
	r.each do |e|
		export << "#{e['FG']}\t#{e['org_name']}\t#{e['alias'].gsub( /\<br\>$/, '' ).gsub( '<br>', ',' )}\t#{e['user']}\t#{e['def_fn']}\n" unless e['org_name'].empty?
	end
	puts "NB2020 [dic] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'memory'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_MEMORY};" )
	r.each do |e|
		content_ = e['content'].gsub( "\n", "<n>" )
		date_ = e['date'].strftime("%Y-%m-%d")
		export << "#{e['code']}\t#{e['user']}\t#{e['category']}\t#{e['pointer']}\t#{content_}\t#{date_}\t#{e['public']}\n"
	end
	puts "NB2020 [memory] data #{@date}\n"
	puts export.force_encoding( 'UTF-8' )

when 'fctp'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_FCTP} INNER JOIN #{$TB_TAG} ON #{$TB_FCTP}.FN = #{$TB_TAG}.FN WHERE #{$TB_TAG}.user='#{ARGV[1]}';" )
	r.each do |e|
		export << "#{e['user']}"
		@fct_item.each do |item|
			if %w( REFUSE ENERC ENERC_KCAL).include?( item )
				export << "\t#{e[item].to_i}"
			else
				export << "\t#{e[item]}"
			end
		end
		export << "\n"
	end
	puts "NB2020 [fctp] data (#{ARGV[1]}) #{@date}\n"
	items = "user"
	@fct_item.each do |item| items << "\t#{item}" end
	puts items + "\n"
	puts export.force_encoding( 'UTF-8' )

when 'tagp'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_TAG} INNER JOIN #{$TB_FCTP} ON #{$TB_TAG}.FN = #{$TB_FCTP}.FN WHERE #{$TB_FCTP}.user='#{ARGV[1]}';" )
	r.each do |e|export << "#{e['FG']}\t#{e['FN']}\t#{e['SID']}\t#{e['SN'].to_i}\t#{e['user']}\t#{e['name']}\t#{e['class1']}\t#{e['class2']}\t#{e['class3']}\t#{e['tag1']}\t#{e['tag2']}\t#{e['tag3']}\t#{e['tag4']}\t#{e['tag5']}\t#{e['status'].to_i}\n" end

	puts "NB2020 [tagp] data (#{ARGV[1]}) #{@date}\n"
	puts "FG\tFN\tSID\tSN\tuser\tname\tclass1\tclass2\tclass3\ttag1\ttag2\ttag3\ttag4\ttag5\tstatus\n"
	puts export.force_encoding( 'UTF-8' )

when 'extp'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_EXT} INNER JOIN #{$TB_TAG} ON #{$TB_EXT}.FN = #{$TB_TAG}.FN WHERE #{$TB_TAG}.user='#{ARGV[1]}';" )
	r.each do |e| export << "#{e['FN']}\t#{e['user']}\t#{e['gycv'].to_i}\t#{e['allergen1'].to_i}\t#{e['allergen2'].to_i}\t#{e['unit']}\n" end

	puts "NB2020 [extp] data (#{ARGV[1]}) #{@date}\n"
	puts "FN\tuser\tgycv\tallergen1\tallergen2\tunit\n"
	puts export.force_encoding( 'UTF-8' )

when 'recipe'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_RECIPE} WHERE user='#{ARGV[1]}';" )
	r.each do |e|
		sum_ = e['sum'].gsub( "\t", "<t>" )
		plotocol_ = e['protocol'].gsub( "\n", "<n>" )
		date_ = e['date'].strftime("%Y-%m-%d")
		export << "#{e['code']}\t#{e['user']}\t#{e['root']}\t#{e['branch'].to_i}\t#{e['public'].to_i}\t#{e['protect'].to_i}\t#{e['draft'].to_i}\t#{e['favorite'].to_i}\t#{e['name']}\t#{e['dish'].to_i}\t#{e['type'].to_i}\t#{e['role'].to_i}\t#{e['tech'].to_i}\t#{e['time'].to_i}\t#{e['cost'].to_i}\t#{sum_}\t#{plotocol_}\t#{date_}\n"
	end

	puts "NB2020 [recipe] data (#{ARGV[1]}) #{@date}\n"
	puts "code\tuser\troot\tbranch\tpublic\tprotect\tdraft\tfavorite\tname\tdish\ttype\trole\ttech\ttime\tcost\tsum\tprotocol\tdate\n"
	puts export.force_encoding( 'UTF-8' )

when 'koyomi'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_KOYOMI} WHERE user='#{ARGV[1]}';" )
	r.each do |e|
		koyomi = e['koyomi'].gsub( "\t", "<t>" ).gsub( "\n", "<n>" )
		export << "#{e['user']}\t#{e['freeze'].to_i}\t#{e['fzcode']}\t#{e['tdiv'].to_i}\t#{koyomi}\t#{e['date']}\n"
	end
	puts "NB2020 [koyomi] data (#{ARGV[1]}) #{@date}\n"
	puts "user\tfreeze\tfzcode\ttdiv\tkoyomi\tdate\n"
	puts export.force_encoding( 'UTF-8' )

when 'koyomiex'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_KOYOMIEX} WHERE user='#{ARGV[1]}';" )
	r.each do |e|
p e
		cell = e['cell']&.gsub( "\t", "<t>" )&.gsub( "\n", "<n>" )
		export << "#{e['user']}\t#{cell}\t#{e['date']}\n" if cell
	end
	puts "NB2020 [koyomiex] data (#{ARGV[1]}) #{@date}\n"
	puts "user\tcell\tdate\n"
	puts export.force_encoding( 'UTF-8' )

when 'fcz'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_FCZ} WHERE user='#{ARGV[1]}';" )
	r.each do |e|
		export << "#{e['code']}\t#{e['origin']}\t#{e['base']}\t#{e['name']}\t#{e['user']}\t#{e['date']}\t#{e['weightp']}"
		@fct_min_nr.each do |item|
			if %w( ENERC ENERC_KCAL ).include?( item )
				export << "\t#{e[item].to_i}"
			else
				export << "\t#{e[item]}"
			end
		end
		export << "\n"
	end
	puts "NB2020 [fcz] data (#{ARGV[1]}) #{@date}\n"
	items = "code\torigin\tbase\tname\tuser\tdate\t'weightp"
	@fct_min_nr.each do |item| items << "\t#{item}" end
	puts items + "\n"
	puts export.force_encoding( 'UTF-8' )

when 'media'
	export = ''
	r = $DB.query( "SELECT * FROM #{$TB_MEDIA} WHERE user='#{ARGV[1]}';" )
	r.each do |e|
		alt_ = e['alt'].gsub( "\n", "<n>" )
		date_ = e['date'].strftime("%Y-%m-%d")
		export << "#{e['user']}\t#{e['code']}\t#{e['origin']}\t#{e['base']}\t#{e['type']}\t#{date_}\t#{e['zidx'].to_i}\t#{alt_}\t#{e['secure'].to_i}\n"
	end

	puts "NB2020 [media] data (#{ARGV[1]}) #{@date}\n"
	puts "user\tcode\torigin\tbase\ttype\tdate\tzidx\talt\tsecure\n"
	puts export.force_encoding( 'UTF-8' )

else
	puts 'Nutrition browser 2020 export 0.0.2 (2024/10/14)'
	puts '[Usage]ruby nb2020-export.rb Exportable data [user]> nb2020-dic.txt'
	puts 'Exportable data list..'
	puts 'unit, gycv, shun, allergen, dic, memory, fctp [], tagp [], extp [], recipe [], koyomi [], koyomiex [], fcz [], media'
end
