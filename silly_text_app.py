'''
Where I apply my library
'''
from silly_text import SillyText
files = ['alabama.txt', 'Arizona.txt', 'georgia.txt', 'illinois.txt', 'massachusetts.txt',
         'oklahoma.txt', 'washington.txt', 'wyoming.txt']

def main():
    print('Homework 7!')
    st = SillyText()
    st.load_text('alabama.txt',label = 'Alabama', policy=True)
    st.load_text('arizona.txt',label='Arizona', policy=True)
    st.load_text('georgia.txt', label='Georgia', policy=True)
    st.load_text('illinois.txt', label='Illinois', policy=True)
    st.load_text('massachusetts.txt', label='Massachussetts', policy=True)
    st.load_text('oklahoma.txt', label='Oklahoma', policy=True)
    st.load_text('washington.txt', label='Washington', policy=True)
    st.load_text('wyoming.txt', label='Wyoming', policy=True)

    # run plots
    st.wordcount_sankey()
    st.readability_plot(policy=True)
    st.vagueness_heatmap()
    print('Done!')



if __name__ == '__main__':
    main()