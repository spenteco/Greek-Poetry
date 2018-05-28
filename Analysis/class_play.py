# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 15:02:20 2018

@author: Anna
"""
from Utilities.stanza_utilities import import_csv
from .class_stanza import Stanza
from .class_StanzaGroup import StanzaGroup

#%%
class Play ():
    def __init__ (self, name, file, directory):
        self.name = name
        self.raw_csv = import_csv(file, directory)
        self.pairs=self._stanza_pairs()
        self._graph_data = None
        
    def _stanza_pairs (self):
        stanza_pairs = []
        for row in self.raw_csv:
            song_num, stanza_name, st_raw, an_raw, meter, notes = row
            name = self.name + '-' + song_num + '-' + stanza_name
            st = Stanza(name, st_raw)
            an = Stanza(name, an_raw)
            pair = StanzaGroup(name, [st, an])
            if meter:
                clean_meter = meter.replace('\n', '')
                meter_list = [m for m in clean_meter]
                pair._meter = meter_list
            pair.notes = notes
            pair.song_number = int(song_num)
            stanza_pairs.append(pair)
        return stanza_pairs
    
    def full_stats (self):
        for p in self.pairs:
            p.print_stats()

    def print_pair_stats_OLD (self):
        comp_list = []
        rep_list = []
        for s in self.pairs:
            included_syls = s.syl_count
            total_matches = s.M1 + s.M2 + s.M3
            total_cons = s.C1 + s.C2 + s.C3
            comp_number = int((total_matches - total_cons)/included_syls * 100)
            comp_list.append(comp_number)
            rep_number = int(s.repeat_percentage *100)
            rep_list.append(rep_number)
            print (s.name)
            print("NUM: " +str(comp_number))
            print("REP: " +str(rep_number))
        #    print(s.repeat_count)
            print()
        print('COMP LIST')
        print(comp_list)
        print('REP LIST')
        print(rep_list)
    
    def display (self):
        syl_count = 0
        match_total = 0
        repeat_total = 0
        for s in self.pairs:
            s.add_stats()
            syl_count += s.syl_count
            match_total += s.M1
            repeat_total += s.repeat_count
            percent_match = int(s.M1/s.syl_count * 100)
            percent_repeat = int(s.repeat_count/s.syl_count * 100)
            print()
            print (s.name)
            if percent_match > 14:
                print("    M1 %  : "+str(percent_match)+ '-- GOOD')
            elif percent_match < 10:
                print("    M1 %  : "+str(percent_match)+ '-- BAD')
            else:
                print("    M1 %  : "+str(percent_match))
            if percent_repeat > 20:
                print("    Rep % : "+str(percent_repeat)+ '-- BAD')
            elif percent_repeat < 14:
                print("    Rep % : "+str(percent_repeat)+ '-- GOOD')
            else:
                print("    Rep % : "+str(percent_repeat))
        match_average = int(match_total/syl_count * 100)
        repeat_average = int(repeat_total/syl_count * 100)
        print()
        print('Average Percent Match: ' + str(match_average))
        print('Average Percent Repetition: ' + str(repeat_average))
   
    def add_stats (self):
        M1 = 0    # All contours are 'DN-A'
        M2 = 0       # All contours are 'DN-A' or 'DN'
        M3 = 0           # All contours are 'UP' or all are 'DN'
        C1 = 0 # Position contains 'DN-A' and 'UP' or '='
        C2 = 0    # Position contains 'UP' and 'DN'
        C3 = 0   # Position contains '=' and 'UP or 'DN'
        M4 = 0    # All other combinations (weak match, since compatible)
        repeats = 0
        syl_count = 0
        for p in self.pairs:
            p.add_stats()
            M1 += p.M1
            M2 += p.M2
            M3 += p.M3
            M4 += p.M4
            C1 += p.C1
            C2 += p.C2
            C3 += p.C3
            repeats += p.repeat_count
            syl_count += p.syl_count
        self.M1 = M1
        self.M2 = M2
        self.M3 = M3
        self.M4 = M4
        self.C1 = C1
        self.C2 = C2
        self.C3 = C3
        self.repeat_count = repeats
        self.syl_count = syl_count
        self.repeat_percentage = repeats/syl_count
        self.match_percentage = M1/syl_count
        
    def print_stat_totals (self):
        self.add_stats()
        print (self.name)
        print("""
              M1 [DN-A]          : {}
              M2 [DN-A, DN]      : {}
              M3 [DN], [UP,UP-G] : {}
              M4 (contains 'N')  : {}
              C3 DN / UP-G       : {}
              C2 DN / UP         : {}
              C1 DN-A /[UP, UP-G]: {}
              
              Repeats : {}
              Repeats/Syls : {}
              
              Matches/Syls : {}""".format(
              self.M1, self.M2, self.M3, self.M4, self.C3, self.C2, self.C1, 
              self.repeat_count, self.repeat_percentage, (self.M1/self.syl_count)))
    
    def graph_data (self, short_name=False):
        if self._graph_data:
            return self._graph_data
        else:
            self.add_stats()
            rows = []
            for p in self.pairs:
                if short_name:
                    stanza_name = p.name.replace(self.name+'-', '')
                else:
                    stanza_name = p.name
                row = [self.name, p.song_number, stanza_name, p.syl_count, p.repeat_percentage, p.match_percentage]
                rows.append(row)
            self._graph_data = rows
            return rows
    def display_graph (self):
        for row in self.graph_data():
            pass
        
    def export_graph_csv (self, directory_name, short_name=False):
        with open(directory_name+self.name+'-graphdata.csv', "w", encoding='utf-8') as output:
            for row in self.graph_data():
                row_text = ','.join([str(x) for x in row]) + '\n'
                output.write(row_text)
    
    def print_graph_csv (self, short_name=False):
        for row in self.graph_data():    
            row_text = ','.join(["\""+str(x)+"\"" for x in row])
            print(row_text)
        
    def export_stats (self, directory_name):
        """Exports the play statistics as a .csv file in the specified directory.
        """
        export_name = self.name
        if export_name.endswith('csv'):
            export_name = export_name[:-4]
        export_name = export_name + '-stats.csv'
        with open(directory_name+export_name, "w", encoding='utf-8') as output:
            for i, s in enumerate(self.pairs):
                quoted_notes = "\"" + s.notes + "\""
                row = [s.name, str(s.syl_count), str(s.M1), str(s.repeat_count), quoted_notes]
                row_text = ','.join(row) + '\n'
                output.write(row_text)
    
    def export_analysis (self, directory_name):
        """Exports the readable display of the entire play to a text file in the
        specified directory.
        """
        export_name = self.name
        if export_name.endswith('csv') or export_name.endswith('txt'):
            export_name = export_name[:-4]
        export_name = export_name + '-analysis.txt'
        with open(directory_name+export_name, "w", encoding='utf-8') as output:
            output.write(self.name + '- Musical Analysis\n')
            for i, s in enumerate(self.pairs):
                output.write('\n\n{}. {}\n\n'.format(i, s.name))
                data = s.display_data()
                for (widths, attributes) in data:
                    for a in attributes:
                        items = [str(i).ljust(width) for width, i in zip(widths, a)]
                        output.write(''.join(items)+'\n')
                    total_length = sum(widths)
                    output.write('-'*total_length + '\n')
        print("Added file '{}' to directory '{}'".format(export_name, directory_name))
            
###########################
        
def get_analysis (name, csv_name, author = 'Aeschylus'):
    play = Play(name, csv_name +'.csv', '..//Corpus/' + author +'/')
    play.export_analysis('..//Corpus/' + author + '/Analyses/')
    return play
        