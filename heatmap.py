
class Heatmap:
    green = ['#f7fcfd', '#e5f5f9', '#ccece6', '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#006d2c', '#00441b',]
    red = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026',]
    red.reverse()

    colors = red + ['#ffffff'] + green
    ranges = [-10, -8, -7, -6, -5, -4, -3, -2, -1, 0,
               1, 2, 3, 4, 5, 6, 7, 8, 10]
    def gen(self, position, cutoff=100):

        colors = []
        for score, piece, squares in zip(position.scores, position.keypieces, position.keysquares):
            if score is None:
                #colors.append('gray')
                continue
            if abs(score) < cutoff:
                continue


            found = False
            score = score / cutoff
            i = 0
            while i < len(self.ranges):
                if score < self.ranges[i]:
                    found = True
                    colors.append(self.colors[i])
                    break
                i = i + 1
            if not found:
                colors.append(self.colors[i-1])
        return colors

    def color(self, score, cutoff=100):
        if score is None:
            return 
        if abs(score) < cutoff:
            return

        score = score / cutoff
        i = 0
        while i < len(self.ranges):
            if score < self.ranges[i]:
                return self.colors[i]
            i = i + 1
        return self.colors[i-1]
