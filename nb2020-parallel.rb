#! /usr/bin/ruby
#encoding: utf-8
#Nutrition browser 2020 parallel foods 0.2.0 (2024/06/29)


#==============================================================================
#LIBRARY
#==============================================================================
require './nb2020-soul'
require './nb2020-local-jp'


#==============================================================================
#STATIC
#==============================================================================
fn_num = 25


#==============================================================================
#DEFINITION
#==============================================================================


#==============================================================================
# Main
#==============================================================================

fn = []
food_name = Hash.new
energy = []
para_fcts = [] 
@fct_para.size.times do
	para_fcts << Array.new
end
fctsn = [] 

#データ読み込み
res = $DB.query( "SELECT FCT.FN, ENERC_KCAL, NAME, #{@fct_para.join( ',' )} FROM #{$MYSQL_TB_FCT} AS FCT LEFT JOIN #{$MYSQL_TB_TAG} AS TAG ON FCT.FN=TAG.FN;" )
res.each do |e|
	fn << e['FN']
	energy = BigDecimal( convert_zero( e['ENERC_KCAL'] ))
	energy = 1 if energy == 0

	@fct_para.each.with_index( 0 ) do |ee, i|
		para_fcts[i] << BigDecimal( convert_zero( e[ee] )) / energy
	end

	food_name[e['FN']] = e['NAME']
end
size_ = fn.size

#正規化
para_fcts.each do |ea|
	sum_ = ea.sum
	mean_ = BigDecimal( sum_ / size_ )

	diff_sq_ = ea.map do |x| ( x - mean_ ) ** 2 end
	sd_ = Math.sqrt( diff_sq_.sum / size_ )
	fctsn << ea.map do |x| (( x - mean_ ) / sd_) end
end

dista = Hash.new
#ユークリッド距離の算出(FLAT)
fn.each.with_index do |e, i|
	base_name = food_name[e]
	dista = {}

	size_.times do |j|
		fn_vs = fn[j]
		target_name = food_name[fn_vs]

		unless base_name == target_name
			d = BigDecimal( 0 )
			@fct_para.size.times do |k|
				d += ( fctsn[k][i] - fctsn[k][j] ) ** 2
			end
			dista[fn[j]] = Math.sqrt( d )
		end
	end

	#距離の近い順にソート
	sorted_dista = dista.sort_by do |_, v| v end

	#重複食品名を除外して上位fn_num個だけにする
	dista_name_fn = Hash.new
	count = 0
	sorted_dista.each do |k, v|
		unless dista_name_fn.key?( food_name[k] )
			dista_name_fn[ food_name[k]] = k
			count += 1
		end
		break if count == fn_num
	end

	near_mem = "flat\t#{e}\t"
	dista_name_fn.each_value do |v|
  		near_mem << "#{v},"
  	end
	near_mem.chop!
	puts near_mem
end

#ユークリッド距離の算出(JUTEN)
@fct_para.each do |juten|
	fn.each.with_index do |e, i|
		base_name = food_name[e]
		dista = {}

		size_.times do |j|
			fn_vs = fn[j]
			target_name = food_name[fn_vs]

			unless base_name == target_name
				d = BigDecimal( 0 )
				@fct_para.each.with_index do |ee, k|
					if juten != ee
						d += ( fctsn[k][i] - fctsn[k][j] ) ** 2
					else
						d += (( fctsn[k][i] - fctsn[k][j] ) * 10 ) ** 2
					end
				end
				dista[fn[j]] = Math.sqrt( d )
			end
		end

		sorted_dista = dista.sort_by do |_, v| v end


		#重複食品名を除外して上位fn_num個だけにする
		dista_name_fn = Hash.new
		count = 0
		sorted_dista.each do |k, v|
			unless dista_name_fn.key?( food_name[k] )
				dista_name_fn[ food_name[k]] = k
				count += 1
			end
			break if count == fn_num
		end

		near_mem = "#{juten}\t#{e}\t"
		dista_name_fn.each_value do |v|
	  		near_mem << "#{v},"
	  	end
		near_mem.chop!
		puts near_mem
	end
end
