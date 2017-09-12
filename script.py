import datetime
import pandas as pd
import urllib2
import time
import os
import os.path
import matplotlib.pyplot as plt
import numpy as np


def promt_time_stamp():
    return str(datetime.datetime.fromtimestamp(time.time()).strftime('[%H:%M:%S] '))


def get_sp500_tickers():
    print(promt_time_stamp() + 'load sp500 tickers ..')
    r = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return r[0][0][1:].tolist()


def download_statistics(tickers, reload=False):
    for ticker in tickers:

        file_name = 'statistics/' + ticker + '.csv'
        if not os.path.exists('statistics/'):
            os.mkdir('statistics/')

        if reload or not os.path.isfile(file_name):
            print(promt_time_stamp() + '(' + ticker + ') downloading statistics ..')

            url = 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker

            try:
                tables =  pd.read_html(url)
                df_temp = pd.concat(tables[1:], ignore_index=True)
                df = pd.DataFrame(df_temp)
                df.set_index(0)
                df = df.rename(columns={1: ticker, 0: 'Values'})

                for index, row in df.iterrows():
                    try:
                        if str(row[ticker]).find('%') > 0:
                            df.set_value(index, ticker, str(row[ticker]).replace('%', ''))  # remove % sign

                        if str(row[ticker]).find('B') > 0:
                            value = float(row[ticker].replace('B', ''))
                            df.set_value(index, ticker, value * 1000)  # convert B to M

                        if str(row[ticker]).find('k') > 0:
                            value = float(row[ticker].replace('k', ''))
                            df.set_value(index, ticker, value / 1000)  # convert k to M

                        if str(row[ticker]).find('M') > 0:
                            df.set_value(index, ticker, str(row[ticker]).replace('M', ''))  # remove M sign

                        s = row['Values'].split(' ')
                        try:
                            x = int(s[len(s) - 1:][0])
                            del s[-1]
                            df.set_value(index, 'Values', ' '.join(s))
                        except Exception:
                            pass

                    except UnicodeEncodeError as u:
                        df.set_value(index, ticker, 'U')

                try:
                    df.to_csv(file_name)
                except (TypeError, UnicodeEncodeError) as e:
                    print(promt_time_stamp() + '(' + url + '): could not store csv file')

            except (urllib2.HTTPError, ValueError) as e:
                print(promt_time_stamp() + str(e))
            time.sleep(1)

        else:
            print(promt_time_stamp() + '(' + ticker + ') already exists ..')


def merge_statistics(tickers):
    print(promt_time_stamp() + 'merge statistics ..')

    main_df = pd.read_csv('statistics/' + tickers[0] + '.csv', index_col=0)

    for ticker in tickers[1:]:
        file_name = 'statistics/' + ticker + '.csv'
        try:
            df = pd.read_csv(file_name)
            main_df = pd.concat([main_df, df[ticker]], axis=1, join='inner')
        except IOError as ie:
            pass

    main_df.to_csv('merged_statistics.csv')


def graph():
    background = '#000606'
    color_labels = '#00decc'

    df = pd.DataFrame(pd.read_csv('merged_statistics.csv', index_col=0))

    # not numerical, dates and empty lines will be droped
    df.drop([1, 7, 8, 9, 10, 54, 55, 56, 57], inplace=True)
    df.fillna(0, inplace=True)

    values = list(df['Values'])
    i = 0
    for v in values:
        print(str(i) + ': ' + str(v))
        i += 1

    # in the cli you can see the index of the statistical values you want to print
    index_of_value = 5

    # graph the first 50 tickers
    objects = list(df)[1:51]
    y_pos = np.arange(len(objects))

    performance = []
    for d in df.values.tolist()[index_of_value][1:51]:
        performance.append(float(d))

    plt.rcdefaults()
    fig, ax = plt.subplots(facecolor=background)

    ax.barh(y_pos, performance, align='center',
            color=color_labels, ecolor=color_labels, facecolor=color_labels)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(objects, color=color_labels)
    ax.invert_yaxis()
    ax.set_title(values[index_of_value], color=color_labels)
    ax.set_facecolor(background)
    ax.tick_params(axis='y', colors=color_labels)
    ax.tick_params(axis='x', colors=color_labels)
    plt.subplots_adjust(left=.06, bottom=.31, right=.98, top=.95, hspace=.0, wspace=.20)

    plt.show()


tickers = get_sp500_tickers()
download_statistics(tickers, reload=False)
merge_statistics(tickers)
graph()
