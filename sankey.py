import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
pio.renderers.default = 'browser'


def stack(df, *cols, vals=None):
    ''' seperate out columns wanted in sankey into pairs if there is a vals
    column apend it, if not set vals equal to one then concat all pairs as
    src and targ, aggregate the df to combine duplicate pairs and sum their
    values and return the stacked dataframe
    df - Dataframe
    cols - dtaframe columns to stack
    vals - Values column (optional)
    '''
    ''' seperate out columns wanted in sankey into pairs if there is a vals
    column apend it, if not set vals equal to one then concat all pairs as
    src and targ, aggregate the df to combine duplicate pairs and sum their
    values and return the stacked dataframe'''
    cols_lst = [*cols]
    pair_list = []
    for i in range(len(cols_lst) - 1):
        # pair by position, rename columns, and add to list
        pair = [cols_lst[i], cols_lst[i + 1]]

        if vals is not None:
            pair_df = df.loc[:, pair + [vals]].copy()

        if vals is None:
            pair_df = df.loc[:, pair].assign(vals=1)

        pair_list.append(pair_df)

    # rename cols
    for pair in pair_list:
        pair.columns = ['src', 'targ', 'vals']

    # concat list of paired data frames
    stacked = pd.concat(pair_list, axis=0)

    # aggregate stacked df and some the related values
    if vals is None:
        stacked = stacked.drop_duplicates(['src', 'targ'], keep='first')
        return stacked

    if vals is not None:
        stacked_agg = stacked.groupby(['src', 'targ'], as_index=False)['vals'].sum()
        return stacked_agg


def _code_mapping(df, src, targ):
    """ Map labels in src and targ columns to integers """
    # unique list of labels for each relationship with the source and target from
    # the df
    labels = pd.concat([df[src], df[targ]]).unique().tolist()

    # Get integer codes for labels
    codes = range(len(labels))

    # Create label to code mapping
    lc_map = dict(zip(labels, codes))

    # Substitute names for codes in dataframe
    new_df = df.copy()
    new_df[src] = new_df[src].map(lc_map)
    new_df[targ] = new_df[targ].map(lc_map)

    # return the new df along with the list of labels that were converted
    return new_df, labels


def make_sankey(df, src, targ, vals,  **kwargs):
    """ Generate a sankey diagram and return the figure
    df - Dataframe
    src - Source column
    targ - Target column
    vals - Values column
    kwargs - optional supported params: pad, thickness, line_color, line_width.
    """

    # Convert column labels to integer codes
    df, labels = _code_mapping(df, src, targ)

    # Extract customizations from kwargs
    pad = kwargs.get('pad', 50)
    thickness = kwargs.get('thickness', 50)
    line_color = kwargs.get('line_color', 'black')
    line_width = kwargs.get('line_width', 0)

    # Construct sankey figure
    link = {
        'source': df[src],
        'target': df[targ],
        'value': df[vals],
        'line': {'color': line_color, 'width': line_width}
    }

    node = {
        'label': labels,
        'pad': pad,
        'thickness': thickness,
        'line': {'color': line_color, 'width': line_width}
    }
    
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)

    return fig


def show_sankey(df, *cols, vals=None, png=None, **kwargs):
    """
    Make AND Show the sankey diagram.   Optionally save it to a file
    df  - The dataframe OR a dict of {word: count}
    cols - columns in df to show in sankey diagram, has to be more than 1
    vals - optional values column (line thickness)
    png  - name of the .png image file to be generated
    kwargs - optional customizations like thickness, line color, etc.
    """
    # allows df to be a dict of {word: count}
    if isinstance(df, dict):
        # make a simple one-level sankey: "root" -> each word
        words = list(df.keys())
        counts = list(df.values())
        sankey_df = pd.DataFrame({
            'src': ['root'] * len(words),
            'targ': words,
            'vals': counts
        })
        fig = make_sankey(sankey_df, 'src', 'targ', 'vals', **kwargs)
    else:
        # original behavior for DataFrame input
        stacked = stack(df, *cols, vals=vals)
        fig = make_sankey(stacked, 'src', 'targ', 'vals', **kwargs)

    fig.show()
    if png:
        fig.write_image(png)