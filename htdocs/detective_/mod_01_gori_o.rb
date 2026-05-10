# Detective module gori 0.1.0 (2026/03/30)
#encoding: utf-8
module DetectiveMod_01_gori_o
  def self.lp( language )
    l = { 'ja' => { mod_name: "ゴリ押し（最大5食品・順番制限あり）" }}
    return l[language]
  end

  def self.calc_score( foods, weights, std_target, sw )
    en = pr = fa = ca = sa = 0
    weights.each_with_index do |w, i|
      en += foods[i]['energy']  * w
      pr += foods[i]['protein'] * w
      fa += foods[i]['fat']     * w
      ca += foods[i]['carb']    * w
      sa += foods[i]['salt']    * w
    end
    ( ( std_target[:energy]  - en ) ** 2 ) * sw[:e] +
    ( ( std_target[:protein] - pr ) ** 2 ) * sw[:p] +
    ( ( std_target[:fat]     - fa ) ** 2 ) * sw[:f] +
    ( ( std_target[:carb]    - ca ) ** 2 ) * sw[:c] +
    ( ( std_target[:salt]    - sa ) ** 2 ) * sw[:s]
  end

  def self.search( foods, foods_size, std_target, sw, depth, prev_w, current_weights, best )
    if depth == foods_size
      score = calc_score( foods, current_weights, std_target, sw )
      if best[:score] < 0 || score < best[:score]
        best[:score] = score
        best[:weights] = current_weights.dup
      end
      return
    end

    w = 0.1
    loop do
      break if w > prev_w

      if depth == foods_size - 1
        w = 100 - current_weights.sum
        break if w <= 0
        break if w > prev_w
        search( foods, foods_size, std_target, sw, depth + 1, w, current_weights + [w], best )
        break
      end

      break if current_weights.sum + w > 100
      search( foods, foods_size, std_target, sw, depth + 1, w, current_weights + [w], best )
      w += 1
    end
  end

  def self.detective_module( foods, std_target, cfg )
    foods = foods.first( 5 )

    total = std_target[:energy] + std_target[:protein] + std_target[:fat] + std_target[:carb] + std_target[:salt]
    sw = {
      e: ( total / ( std_target[:energy]  == 0 ? 0.1 : std_target[:energy]  ) ) ** 2,
      p: ( total / ( std_target[:protein] == 0 ? 0.1 : std_target[:protein] ) ) ** 2,
      f: ( total / ( std_target[:fat]     == 0 ? 0.1 : std_target[:fat]     ) ) ** 2,
      c: ( total / ( std_target[:carb]    == 0 ? 0.1 : std_target[:carb]    ) ) ** 2,
      s: ( total / ( std_target[:salt]    == 0 ? 0.1 : std_target[:salt]    ) ) ** 2
    }

    best = { score: -1, weights: Array.new( foods.size, 0 ) }
    search( foods, foods.size, std_target, sw, 0, 100, [], best )

    best[:weights]
  end
end
