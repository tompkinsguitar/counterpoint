'''
    Author: Daniel C. Tompkins
    Email: tompkinsguitar@gmail.com
    
    Please feel free to use this as you wish, and I welcome any feedback.
'''


import random

from music21 import *
import numpy as np
from scipy.stats import entropy


class CounterPoint:
    perfect_intervals = (0, 7, 12)
    illegal_intervals = (1, 2, 5, 6, 10, 11)
    thirds = (3, 4)
    sixths = (8, 9)

    diatonic_pcs = (0, 2, 4, 5, 7, 9, 11)
    chromatic_pcs = (1, 3, 6, 8, 10)

    illegal_skips = range(9, 12)


    pc_modes = {
        'ionian': (0, (11, 2)),
        'dorian': (2, (1, 4)),
        'phrygian': (4, (2, 5)),
        'lydian': (5, (4, 7)),
        'mixolydian': (7, (6, 9)),
        'aeolian': (9, (8, 11))
    }

    clefs = {'treble': range(57, 79), 'bass': range(45, 64)}

    # def __init__(self, mode='ionian', length=6, clef='treble'):
    #     self.mode = mode
    #     self.length = length
    #     self.clef = clef

    def melody_maker(self, clef='treble', length=6, mode='ionian',
                     zenith_threshold=1, nadir_threshold=1):
        # clef = self.clef
        # length = self.length
        # mode = self.mode
        '''find all possible notes'''
        mel = [0 for x in range(length)]
        possible_notes = []
        possible_cadences = []
        for x in self.clefs[clef]:
            if x%12 in self.diatonic_pcs:
                possible_notes.append(x)
            if x%12 in self.pc_modes[mode][1]:
                possible_cadences.append(x)
        possible_notes = random.sample(possible_notes, len(possible_notes))

        '''make the cadence'''
        possible_cadences = random.sample(possible_cadences, len(possible_cadences))
        possible_final = []
        possible_penultimate = []
        for x in possible_notes:
            if x%12 == self.pc_modes[mode][0]:
                possible_final.append(x)
        thefinal = random.choice(possible_final)
        mel[0] = thefinal
        mel[-1] = thefinal
        for x in possible_cadences:
            if abs(x-thefinal) <= 4:
                possible_penultimate.append(x)
        mel[-2] = random.choice(possible_penultimate)

        for n in range(1, len(mel[:-2])):
            next_note = []
            for nn in possible_notes:
                if nn != mel[n-1]: #no repeated notes
                    if abs(nn - mel[n-1]) not in self.illegal_skips: #no illegal skips
                        if n == len(mel[1:-2]):
                            if mel[-2] in self.chromatic_pcs: #check for augmented second
                                if mel[-2] - nn < 3: #and leap into chromatic note
                                    next_note.append(nn)
                            elif abs(mel[-2] - nn) <= 4:
                                next_note.append(nn)
                        else:
                            next_note.append(nn)
            mel[n]=random.choice(next_note)
        while self.check_melody(mel=mel, mode=mode,
                                zenith_threshold=zenith_threshold, nadir_threshold=nadir_threshold) is False:
            mel = self.melody_maker()
        return mel


    def check_melody(self, mel, mode='ionian', zenith_threshold=1, nadir_threshold=1):
        if mel[0] != mel[-1]:
            # print('it was the first and last note')
            return False
        elif mel[-2]%12 not in self.pc_modes[mode][-1]:
            # print('penultimate')
            return False
        for x in range(1, len(mel)):
            if mel[x - 1] == mel[x]:
                # print('consecutive', mel[x-1], mel[x])
                return False

            interval = abs(mel[x] - mel[x - 1])


            if interval in range(10, 12) or interval > 12:
                # print('leap too big', mel[x], mel[x-1], interval)
                return False
            elif interval == 6:
                # print('tritone')
                return False
            elif mel[x] % 12 not in self.diatonic_pcs and mel[x] - mel[x - 1] == 3:
                # print(mel[x]%12, mel[x-1]%12, mel[x] - mel[x-1])
                # print('augmented second')
                return False
            elif mel[x] % 12 not in self.diatonic_pcs and abs(mel[x] - mel[x - 1]) % 12 > 4:
                # print('leap into dissonance', mel[x] % 12, mel[x - 1] % 12, abs(mel[x] - mel[x - 1]) % 12)
                return False
            elif x != len(mel):
                if interval > 4 and abs(mel[x+1] - mel[x]) > 4:
                    # print('too leap-y')
                    return False
        zenith = 0
        nadir = 0
        for x in mel[1:-1]:
            if x == max(mel):
                zenith += 1
            elif x == min(mel):
                nadir += 1
        if nadir > nadir_threshold:
            # print('it was the nadir', min(mel), nadir)
            return False
        if zenith > zenith_threshold:
            # print('it was the zenith', max(mel), zenith)
            return False
        # self.melody.append(mel)
        return True

    def counterpoint_checker(self, cf, cpt):
        all_intervals = []
        score_dict = {'distance': 0, 'style': 0, 'melodic_entropy': 0, 'harmonic_entropy': 0}
        
        intervals = np.array(cpt) - np.array(cf)

        thirds_counter = 0
        sixths_counter = 0
        upward_motion = 0
        downward_motion = 0
        #check first octave
        if intervals[0] % 12 != 0:
            score_dict['distance'] = 0
            return False, score_dict

        score_dict['distance'] += 1

        if len(cf) < 2:
            return True, score_dict

        #check intervals
        interval_step = 0
        for interval, cpt_note, cf_note in zip(intervals[1:], cpt[1:], cf[1:]):
            # print(interval_step, interval)
            prev_interval = intervals[interval_step]
            if interval >= 20 or interval < 0:  # range issues
                # print('range issues', interval)
                return False, score_dict
            elif interval % 12 in self.illegal_intervals:  # illegal harmonic interval
                # print('illegal interval', interval, interval % 12)
                return False, score_dict
            elif interval in self.perfect_intervals and prev_interval in self.perfect_intervals:  # parallel perfects
                # print('consecutive perfects', interval, prev_interval)
                return False, score_dict
            elif interval % 12 == 7 and prev_interval % 12 == 7:  # parallel fifths
                # print('consecutive fifths', interval, prev_interval)
                return False, score_dict
            elif interval % 12 == 0 and prev_interval % 12 == 0:  # parallel octaves
                # print('consecutive fifths', interval, prev_interval)
                return False, score_dict
            elif prev_interval in self.perfect_intervals \
                    and cpt_note - cpt[interval_step] > 2 \
                    and cf_note - cf[interval_step] > 2:
                # print('direct perfects')
                return False, score_dict
            if interval in self.thirds:
                thirds_counter += 1
                if thirds_counter >= 4:
                    # print('too many thirds')
                    return False, score_dict
            else:
                thirds_counter = 0
            if interval in self.sixths:
                sixths_counter += 1
                if sixths_counter >= 4:
                    # print('too many sixths')
                    return False, score_dict
            else:
                sixths_counter = 0
            if cpt_note > cpt[interval_step] and cf_note > cf[interval_step]:  # no contrary motion
                upward_motion += 1
                downward_motion = 0
            if upward_motion > 3:
                # print('upward motion')
                return False, score_dict
            elif cpt_note < cpt[interval_step] and cf_note < cf[interval_step]:
                upward_motion = 0
                downward_motion += 1
            if downward_motion > 3:
                # print('downward motion')
                return False, score_dict
            # leap in same direction
            if cpt[interval_step] - cpt_note > 3 and cf[interval_step] - cf_note > 3:
                # print('leap same direction')
                return False, score_dict
            elif cpt_note - cpt[interval_step] > 3 and cf_note - cf[interval_step] > 3:
                # print('leap same direction')
                return False, score_dict

            score_dict['distance'] += 1
            interval_step += 1
            
        if len(cpt) != len(cf):
            score_dict['melodic_entropy'] = entropy(cpt) / len(cpt)
            score_dict['harmonic_entropy'] = entropy(intervals) / len(intervals)
            return True, score_dict
        if abs(cf[-2] - cf[-1]) > 2 and abs(cpt[-2] - cpt[-1]) > 2:  # cadence
            # print('cadence intervals')
            return False, score_dict
        elif abs(cf[-2] - cf[-1]) > 7 or abs(cpt[-2] - cpt[-1]) > 7:
            # print('cadence intervals')
            return False, score_dict
        
        #check cross relations at cadence
        elif cf[-2] % 12 in self.chromatic_pcs and cpt[-3] % 12 == cf[-2] % 12 - 1:  # cross relations
            # print('cross relation')
            return False, score_dict
        elif cpt[-2] % 12 in self.chromatic_pcs and cf[-3] % 12 == cpt[-2] % 12 - 1:
            # print('cross relation')
            return False, score_dict
        elif cf[-2] % 12 in self.chromatic_pcs and cf[-3] % 12 == cf[-2] % 12 - 1:  # cross relations
            # print('cross relation')
            return False, score_dict
        elif cpt[-2] % 12 in self.chromatic_pcs and cpt[-3] % 12 == cpt[-2] % 12 - 1:
            # print('cross relation')
            return False, score_dict
        
        #check final octave
        if intervals[-1] % 12 != 0:
            score_dict['distance'] -= 1
            return False, score_dict
        # if 0 in intervals[1:-1]:
        #     score_dict['distance'] = np.where(intervals[1:-1] == 0)[0][0]
        #     return False, score_dict
        score_dict['melodic_entropy'] = entropy(cpt) / len(cpt)
        score_dict['harmonic_entropy'] = entropy(intervals) / len(intervals)
        return True, score_dict

    def make_counterpoint(self, length=6, mode='ionian',
                          cf_clef='bass', cpt_clef='treble',
                          nadir_threshold=1, zenith_threshold=1):
        cpt = self.melody_maker(length=length, mode=mode, clef=cpt_clef,
                                zenith_threshold=zenith_threshold,
                                nadir_threshold=nadir_threshold)
        cf = self.melody_maker(length=length, mode=mode, clef=cf_clef,
                               zenith_threshold=zenith_threshold,
                               nadir_threshold=nadir_threshold)

        # while self.check_melody(cpt) is False:
        #     cpt = self.melody_maker(length=length, mode=mode, clef=cf_clef,
        #                            zenith_threshold=zenith_threshold,
        #                            nadir_threshold=nadir_threshold)
        #
        # while self.check_melody(cf) is False:
        #     cf = self.melody_maker(length=length, mode=mode, clef=cf_clef,
        #                            zenith_threshold=zenith_threshold,
        #                            nadir_threshold=nadir_threshold)

        if len(cf) != len(cpt):
            raise ValueError('Cantus and Counterpoint melodies must be the same length')
        trial_counterpoint = self.counterpoint_checker(cf=cf, cpt=cpt)
        cf_trial = 0
        while trial_counterpoint[0] is False:
            print(trial_counterpoint)
            cf_trial += 1
            
            if cf_trial == 200:
                zenith_threshold += 1
                nadir_threshold += 1
            elif cf_trial == 400:
                zenith_threshold += 1
                nadir_threshold += 1
            elif cf_trial == 600:
                zenith_threshold += 1
                nadir_threshold += 1
            elif cf_trial == 800:
                zenith_threshold += 1
                nadir_threshold += 1
            cpt = self.melody_maker(length=length, mode=mode, clef=cpt_clef, nadir_threshold=nadir_threshold,
                                    zenith_threshold=zenith_threshold)
            if cf_trial == 999:
                print('trying new cf()()()()()()()()()()()()()()()()()()()()()()()')
                cf = self.melody_maker(length=length, mode=mode, clef=cf_clef, nadir_threshold=nadir_threshold,
                                       zenith_threshold=zenith_threshold)
                cf_trial = 0
                zenith_threshold = 1
                nadir_threshold = 1
            trial_counterpoint = self.counterpoint_checker(cf=cf, cpt=cpt)
            print(trial_counterpoint)
        return {'counterpoint': cpt, 'cantus': cf}


if __name__ == '__main__':

    from time import time

    st = time()

    #This ensures leading tones with sharps rather than enharmonic spellings
    notes = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'B-', 11: 'B'}
    octaves = {'2': [x for x in range(36, 36+12)],
               '3': [x for x in range(48, 48 + 12)],
               '4': [x for x in range(60, 60 + 12)],
               '5': [x for x in range(72, 72 + 12)]}

    C = CounterPoint()

    cantus = stream.Part(id='cantus')
    counterpoint = stream.Part(id='counterpoint')

    '''
    this is where you input what parameters you want
    WARNING: at this time, if length > 9, it takes a long time to finish
    '''
    final_cpt = C.make_counterpoint(mode='phrygian', cf_clef='bass', cpt_clef='treble',
                                    length=6, zenith_threshold=1, nadir_threshold=1)

    '''
    This puts everything on a score. If there is an error, make sure you 
    have music21's environment settings pointed to your notation software.
    I recommend musescore. Music21 tries to find the software, but if there is an error:
    
    in python, type:
    from music21 import *
    us = environment.UserSettings()
    us.create() #you might not have to do this
    us['musicxmlPath'] = '/Applications/MuseScore 2.app'
    '''

    print(final_cpt['counterpoint'], 'counterpoint')
    print(final_cpt['cantus'], 'cantus')
    for x in final_cpt['cantus']:  # cf
        c_note = notes[x % 12]
        c_octave = ''
        for a, b in octaves.items():
            if x in b:
                c_octave = a
        cantus.append(note.Note(c_note + c_octave, type='whole'))

    for x in final_cpt['counterpoint']:  # ctpt
        c_note = notes[x % 12]
        c_octave = ''
        for a, b in octaves.items():
            if x in b:
                c_octave = a
        counterpoint.append(note.Note(c_note + c_octave, type='whole'))

    S = stream.Score()
    S.insert(counterpoint)
    S.insert(cantus)
    print('finished in', time() - st, 'seconds')
    S.show()

