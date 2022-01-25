import re
from itertools import chain
import json 
import os
from collections import Counter
import pandas as pd

notes_sharp = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
notes_flat = ["A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]

major_scale = [0,2,4,5,7,9,11]
minor_scale = [0,2,3,5,7,8,10]

numerals_major = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
numerals_minor = ["i", "ii°", "III", "iv", "v", "VI", "VII"]
numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii"]

# get only the letter and if it's major/minor
def clean_chord(chord):
    # remove bass note notation
    if "/" in chord:
        chord = chord.split("/")[0]
        
    #TODO what if it's capitals???? 
    # remove any adds
    if "add" in chord:
        chord = chord.split("add")[0]
        
    # remove any sus
    if "sus" in chord:
        chord = chord.split("sus")[0]
        
    # remove numbers
    chord = ''.join([i for i in chord if not i.isdigit()])
    
    return(chord)
    
# later on i might want this info
def clean_chord_complex(chord):
    chord_dict = {}
    
    chord_dict['base chord'] = ''.join([i for i in chord.split("/")[0].split("add")[0].split("sus")[0] if not i.isdigit()])
    
    if "/" in chord:
        chord_dict['bass note'] = chord.split("/")[1]
        
    # remove any adds
    if "add" in chord:
        chord_dict['add'] = chord.split("add")[1]
        
    # remove any sus
    if "sus" in chord:
        chord_dict['sus'] = chord.split("sus")[1]
        
    #TODO get like 6/7 they sometimes don't have add before them
    return(chord_dict)

# get a dict of all the chords in the song and their occurrences
def get_all_chords(chord_progression):
    chords = [chord_progression[x]['chords'][1:-1] for x in chord_progression]
    chords = list(chain.from_iterable(chords))
    return (Counter(chords))

#TODO: eventually need to include logic for harmonic/melodic minor
# find the best-fit tonic 
def infer_tonic(chord_dict):
    # all chords in the song
    song_chords = [x for x in chord_dict]
    
    # possible chords
    all_chords = {}
    
    # create dictionary mapping each chord to the number of unique chords in the song that are in that key
    for chord in chord_dict:
        # diminished and augmented chords are not tonics
        if 'dim' in chord or 'aug' in chord:
            continue
        songs_in_key = sum([1 for x in song_chords if x in get_chords(chord)])
        all_chords[chord] = songs_in_key
    
    # how many chords are in the best fit key(s)?
#     max_value = max(all_chords.items(), key=lambda x : x[1])
    max_value = max([all_chords[key] for key in all_chords])
    
    # get list of possible keys that match this value
    best_fit_chords = [key for key in all_chords if all_chords[key] == max_value]
    
    # if there's only one, print that:
    if len(best_fit_chords) == 1:
        return best_fit_chords[0]
    else:
        # right now implementing logic to return the major over the minor since *most* popular songs are in a major key
        # TODO: in the future it might make more sense to use the most commonly occuring chord or something similar
        non_minor_fits = [key for key in best_fit_chords if "m" not in key]
        
        if len(non_minor_fits) > 0:
            # if there are one or more possible non-minor fits, pick the first one
            return non_minor_fits[0]
        else:
            # if there are no fits that aren't minor, just pick the first one
            return best_fit_chords[0]

def apply_capo(orig_key, capo):
    # strip major/minor marking at end
    note = orig_key.split("m")[0]
    
    append = ""
    if orig_key.endswith("m") or "inor" in orig_key:
        append = "m"
    

    
    if (note.endswith("#")):
        orig_loc = notes_sharp.index(note) 
        return(notes_sharp[(orig_loc + capo)%12] + append)
    elif (note.endswith("b")):
        orig_loc = notes_flat.index(note)
        return(notes_flat[(orig_loc + capo)%12] + append)
    else: #todo eventually we should choose flat vs. sharp based on what's in the tabs 
        orig_loc = notes_sharp.index(note)
        return(notes_sharp[(orig_loc + capo)%12] + append)
    
def get_notes(key):
    # by default we assume major, but change to minor scale if indicated
    idx = major_scale
    if key.endswith("m"):
        idx = minor_scale
    
    # by default we assume we're working with sharps, but change to flats if indicated
    notes = notes_sharp
    if flats_or_sharps(key) == "b":
        notes = notes_flat
    
    loc = notes.index(key.split("m")[0])
    return [notes[(i+loc)%12] for i in idx]


def get_chords(key):
    notes = get_notes(key)
    
    #TODO: currently just works with natural minor, edit to include chords that are in harmonic & melodic minors
    if key.endswith("m"):
        notes[0] = notes[0]+"m"
        notes[1] = notes[1]+"dim"
        notes[3] = notes[3]+"m"
        notes[4] = notes[4]+"m"
    else:
        notes[1] = notes[1]+"m"
        notes[2] = notes[2]+"m"
        notes[5] = notes[5]+"m"
        notes[6] = notes[6]+"dim"
    
    return(notes)

def get_relation(key, chord):
    chords = get_chords(key)
    
    if chord in chords:
        if key.endswith("m"):
            return numerals_minor[chords.index(chord)]
        else:
            return numerals_major[chords.index(chord)]
    else:
        # flat or sharp (very important apparently)
        flat_or_sharp = flats_or_sharps(key)
        
        # trim minor
        tonic_note = key.split("m")[0]
        # chord can be minor or diminished
        chord_note = convert_note(chord.split("m")[0].split("d")[0], flat_or_sharp)
        
        # if the NOTE is in the key signature but the chord isn't, that's easy.
        notes_in_key_sig = get_notes(key)
#         print("Chord Note: " + chord_note)
#         print("Notes in Key Sig: " + " ".join(notes_in_key_sig))
        if chord_note in notes_in_key_sig:
            # identify what number it is in the key signature
            my_num = numerals[notes_in_key_sig.index(chord_note)]
            
            if "dim" in chord:
                return my_num + "°"
            elif chord.endswith("m"):
                return my_num 
            else:
                return my_num.upper()
        
        # if the NOTE isn't in the key signature, then that's a bit more work
        else:
            # if tonic uses sharps
            if flat_or_sharp == "#":
            
                # find numeric for item one index lower in sharp notes
                one_note_lower = notes_sharp[(notes_sharp.index(convert_note(chord_note,flat_or_sharp)) - 1) % 12]
                my_num = numerals[notes_in_key_sig.index(one_note_lower)]
                
                if "dim" in chord:
                    return "#" + my_num + "°"
                elif chord.endswith("m"):
                    return "#" + my_num 
                else:
                    return "#" + my_num.upper()
                
            else:
                # find numeric for item one index higher in sharp notes
                one_note_higher = notes_flat[(notes_flat.index(convert_note(chord_note,flat_or_sharp)) + 1) % 12]
                my_num = numerals[notes_in_key_sig.index(one_note_higher)]
                
                if "dim" in chord:
                    return "b" + my_num + "°"
                elif chord.endswith("m"):
                    return "b" + my_num 
                else:
                    return "b" + my_num.upper()
                
            
        
        
# get rid of numbers and such in region label
def clean_region(rname):
    rname = rname.lower()
    
    return ''.join([i for i in rname if not i.isdigit()]).strip()

# obtain structure dict for a list of files\
def get_structure_dict(file_list):
    structure_dict = {}

    for fname in file_list:
        with open(fname) as json_file:
            data = json.load(json_file)

        sections = ["StartOfSong"]
        sections.extend([clean_region(data[x]['type'][1:-1]) for x in data])
        sections.append("EndOfSong")

        for i in range(len(sections)-1):
            if sections[i] not in structure_dict:
                structure_dict[sections[i]] = {}

            if sections[i+1] not in structure_dict[sections[i]]:
                structure_dict[sections[i]][sections[i+1]] = 1
            else:
                structure_dict[sections[i]][sections[i+1]] += 1
                
    return (structure_dict)
    
def clean_structure_dict(structure_dict, maximum):
    # if a value is only in here once it's probably specialized to the tab it was taken from
    
    unique_values = []
    
    for region_id in structure_dict:
        sub_dict = structure_dict[region_id]
        
        # get the number of regions it maps after
        total_values = sum([sub_dict[k] for k in sub_dict])
        
        # if the total occurrences of the region is less than or equal to the maxium, add to list
        if total_values <= maximum:
            unique_values.append(region_id)
            
    
    # if there are no unique values then just return the dict
    if len(unique_values) == 0:
        return (structure_dict)
    
    # remove all unique values from sub dictionaries
    for region_id in structure_dict:
        for val_to_remove in unique_values:
            if val_to_remove in structure_dict[region_id]:
                structure_dict[region_id].pop(val_to_remove)
            
    # remove all unique values from the main dictionary
    for val_to_remove in unique_values:
        structure_dict.pop(val_to_remove)

    return(structure_dict)

# get statistics about distribution and variety of song sections
def get_count_stats(file_list):
    structure_dict = {
        'total_num_sections' : [],
        'num_unique_sections' : []
    }

    for fname in file_list:
        with open(fname) as json_file:
            data = json.load(json_file)
            
            sections = [clean_region(data[x]['type'][1:-1]) for x in data]
            
            structure_dict['total_num_sections'].append(len(sections))
            structure_dict['num_unique_sections'].append(len(list(set(sections))))
    
    return (structure_dict)

# obtain structure dict for a list of files\
def get_chord_structure_dict(file_list):
    # this will have section types as a key and then a sub dictionary
    # in the sub dictionary each key is a start chord and there's a dictionary of occurrences of subsequent notes
    structure_dict = {}

    for fname in file_list:
        with open(fname) as json_file:
            data = json.load(json_file)


        # iterate over each section in a single song
        for key in data:
            
            section = clean_region(data[key]['type'][1:-1])
            
            # if we haven't seen a section like this before, add a list for it 
            if section not in structure_dict:
                structure_dict[section] = {}
            
            # iterate over the list of chords
            for i in range(len(data[key]['chords_numeric'])-1):
                current_chord = data[key]['chords_numeric'][i]
                next_chord = data[key]['chords_numeric'][i+1]
                                
                if current_chord not in structure_dict[section]:
                    structure_dict[section][current_chord] = {}
                    
                if next_chord not in structure_dict[section][current_chord]:
                    structure_dict[section][current_chord][next_chord] = 1
                else:
                    structure_dict[section][current_chord][next_chord] += 1
                
    return (structure_dict)


def flats_or_sharps(key_sig):
    if "b" in key_sig:
        return("b")
    elif "#" in key_sig:
        return("#")
    elif key_sig in ["C", "Cm", "Dm", "F", "Fm", "Gm"]:
        return("b")
    else:
        return("#")
    
def convert_note(note, end):
    whitekey_aliases = {"Fb": "E",
                  "E#": "F",
                  "Cb": "B",
                  "B#": "C"}
    if end=="":
        return whitekey_aliases[note]
    elif end=="#":
        if note in notes_sharp:
            return note
        else:
            return notes_sharp[notes_flat.index(note)]
    elif end=="b":
        if note in notes_flat:
            return note
        else:
            return notes_flat[notes_sharp.index(note)]
    else:
        return note
    
    
