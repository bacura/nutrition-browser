#! /usr/bin/ruby
#nb2020-wcr.rb

#Bacura KYOTO Lab
#Saga Ukyo-ku Kyoto, JAPAN
#https://bacura.jp
#yossy@bacura.jp


#==============================================================================
# MAIN
#==============================================================================

source_file = '20201225-mxt_kagsei-mext_01110_011_ow.txt'
out_file = 'nb2020-wcr.txt'

data_solid = ''
page = 34
# 食品成分表データの読み込みと加工
f = open( source_file, 'r' )
f.each_line do |e|
	line = e.force_encoding( 'UTF-8' ).chomp

	if /^\d\d\d\d\d/ =~ line
		data_solid << line.scan( /^\d\d\d\d\d/ ).first
		data_solid << "\t"
		if /[\-|\d]+$/ =~ line
			data_solid << line.scan( /[\-|\d]+$/ ).first.sub( '-', '' )
			data_solid << "\n"
		end
	elsif  /^[\-|\d]+$/ =~ line
		if line.to_i == page
			page += 1
		else
			data_solid << line.scan( /^[\-|\d]+$/ ).first.sub( '-', '' )
			data_solid << "\n"
		end
	elsif  /[\-|\d]+$/ =~ line
		if line.to_i == page
			page += 1
		else
			data_solid << line.scan( /[\-|\d]+$/ ).first.sub( '-', '' )
			data_solid << "\n"
		end
	end

end
f.close


# 成分表データの書き込み
f = open( out_file, 'w' )
f.puts data_solid
f.close

