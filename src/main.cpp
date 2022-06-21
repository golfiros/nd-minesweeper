#include <iostream>
#include <cstdint>
#include <cmath>

float rand_float(){
    return ((float) rand()) / (float) RAND_MAX;
}

class Board {
public:
    Board(uint8_t dim, uint32_t len, float dens) {
        dimension = dim;
        length = len;
        density = dens;

        pows_len = (uint32_t*)malloc(3 * dimension * sizeof(uint32_t));
        pows_len[0] = 1;
        pows_three = pows_len + dimension;
        pows_three[0] = 1;
        coord_buff = pows_three + dimension;

        for(int i=1;i<dimension;i++){
            pows_len[i] = length * pows_len[i - 1];
            pows_three[i] = 3 * pows_three[i - 1];
        }

        sites = length * pows_len[dimension - 1];
        hypercube = 3 * pows_three[dimension - 1];
        
        board = (int32_t*)calloc(sites, sizeof(int32_t)); 
        for(int i=0;i<sites;i++){
            if(rand_float() < density){ 
                board[i] = -hypercube; 
                mines++; 
                for(int j=1;j<hypercube;j++){ 
                    uint32_t site = 0;
                    for(int k=0;k<dimension;k++){
                        site += ((length + i / pows_len[k] + ((j / pows_three[k] + 1) % 3) - 1) % length) * pows_len[k];
                    }
                    board[site] += 1;
                }
            }
        }
        //printf("%d %f\n", mines, float(mines)/float(sites));
    }
    ~Board(){
        free(board);
        free(pows_len);
    }

    void print(){
        if(dimension!=2){ return; }
        for(int i=0;i<length;i++){
            for(int j=0;j<length;j++){
                int index = i * length + j;
                if(board[index]<0){ board[index] = -1; }
                printf("%d\t", board[index]);
            }
            printf("\n");
        }
    }
private:
    int32_t* board;

    uint8_t dimension;
    uint32_t length;
    float density;

    uint32_t sites;
    uint32_t hypercube;
    uint32_t mines = 0;

    uint32_t* pows_len;
    uint32_t* pows_three;
    uint32_t* coord_buff;
};

int main(int argc, char** argv) {
    {
        int s;
        FILE *f;
        f = fopen("/dev/urandom", "rb");
        fread(&s, sizeof(int), 1, f);
        fclose(f);
        srand(s);
    }

    if(argc < 4) {
        printf("missing arguments (dim len dens)");
        return -1;
    }

    Board board = Board(atoi(argv[1]),atoi(argv[2]),atof(argv[3]));
    board.print();

    return 0;
}