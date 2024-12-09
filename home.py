import json
from email.policy import default

import streamlit as st
import random
import time

from streamlit import session_state

# Load the list of words
with open("./listes_mots/liste_01.json", "r") as f:
    word_lists = json.load(f)

# Sidebar settings
display_duration = st.sidebar.slider(
    "Combien de temps le mot doit-il être affiché ?",
    min_value=0.1, max_value=6.0, value=2.0, step=0.1
)

# Initialize session state
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "nombre_de_reussites" not in st.session_state:
    st.session_state.nombre_de_reussites = 0
if "shuffled_list" not in st.session_state:
    st.session_state["shuffled_list"] = []
if "mode" not in st.session_state:
    # "showing_word" or "feedback"
    st.session_state.mode = "showing_word"
if "session_started" not in session_state:
    st.session_state["session_started"] = False
if "current_word_list" not in st.session_state:
    st.session_state["current_word_list"] = []
if "shuffling_done" not in st.session_state:
    st.session_state["shuffling_done"] = False
if "slk" not in st.session_state:
    st.session_state["slk"] = []
    st.session_state["shuffling_done"] = False

name = st.sidebar.text_input("Quel est ton nom ?")
selected_list_keys = st.sidebar.multiselect("Selectionne une ou plusieurs liste(s) de mots", word_lists.keys())
if selected_list_keys != st.session_state["slk"]:
    st.session_state["slk"] = selected_list_keys
    st.session_state["shuffling_done"] = False

for wlk in st.session_state["slk"]:
    if name != "":
        st.session_state["current_word_list"].append(name)
    st.session_state["current_word_list"] += word_lists[wlk]
    st.session_state["current_word_list"] = list(set(st.session_state["current_word_list"]))
if len(st.session_state["current_word_list"]) > 0 and not st.session_state["shuffling_done"]:
    random.shuffle(st.session_state["current_word_list"])
    st.session_state["shuffled_list"] = list(set(st.session_state["current_word_list"]))
    st.session_state["shuffling_done"] = True

if len(st.session_state["shuffled_list"]) > 1:
    current_index = st.session_state.current_index
    st.sidebar.progress(current_index/len(st.session_state["shuffled_list"]))

    if not st.session_state["session_started"]:
        if st.button("Commencer"):
            st.session_state["session_started"] = True
    else:
        if st.button("Recommencer du début"):
            st.session_state["session_started"] = False
            st.session_state.current_index = 0
            st.session_state.nombre_de_reussites = 0
            st.session_state["shuffled_list"] = []
            st.session_state.shuffled_list = st.session_state["current_word_list"]
            st.session_state.mode = "showing_word"
            st.session_state["session_started"] = False
            st.session_state["current_word_list"] = []
            st.session_state["shuffling_done"] = False
            st.rerun()

    display_zone = st.empty()

    if st.session_state["session_started"]:
        # If we've gone through all words, end the session
        if current_index >= len(st.session_state["shuffled_list"]):
            st.write("Session terminée !")
            st.write("Nombre de réussites : {} sur {}".format(st.session_state.nombre_de_reussites, len(st.session_state["shuffled_list"])))
            if st.session_state.nombre_de_reussites == len(st.session_state["shuffled_list"]):
                st.balloons()
            st.stop()

        word = st.session_state["shuffled_list"][current_index]

        if st.session_state.mode == "showing_word":
            # Show the word
            display_zone.markdown("""
            ---------------------------------
            
            # {}
            
            ----------------------------------
            """.format(word))

            # Wait for the specified duration
            time.sleep(display_duration)

            # After waiting, switch to feedback mode
            st.session_state.mode = "feedback"
            st.rerun()

        elif st.session_state.mode == "feedback":
            # Clear the word and show blank space + buttons
            display_zone.markdown("""
                ---------------------------------
                
                # {}
                
                ----------------------------------
                """.format("..."))

            feedback_zone = st.empty()
            if st.session_state.mode == "feedback":
                col1, col2 = feedback_zone.columns(2)
                feedback_given = False
                with col1:
                    if st.button("😊 J'ai réussi à lire le mot"):
                        st.session_state.nombre_de_reussites += 1
                        st.session_state.current_index += 1
                        st.session_state.mode = "showing_word"
                        feedback_given = True

                with col2:
                    if st.button("🙁 Je n'ai pas réussi à lire le mot"):
                        st.session_state.current_index += 1
                        st.session_state.mode = "showing_word"
                        feedback_given = True

                if feedback_given:
                    if st.button("Mot suivant") and feedback_given:
                        feedback_zone.write(" ")
                        st.rerun()
