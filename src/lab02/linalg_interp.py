import numpy as np

def gauss_iter_solve(A,b,x0=None,tol=1e-8,alg="seidel"):
    """
    Description of function.
        Parameters
        A: Coefficient Matrix (nxn) (array-like) 
        b: Right Hand Side Vector (mxn) (array-like)
        x0: Optional initial guess, defaults to all 0s (array-like)
        tol: Error tolerance, defaults to 1e-8 (mxn) (float)
        alg: Optional choice of algorithm, defaults to seidel (string)
        ----------
        Returns
        x: Solution to matrix (mxn) (array-like)
        -------
    """
    #makes sure A and b are numpy arrays
    A=np.array(A, dtype=float)
    b=np.array(b, dtype=float)
    #creation of initial guess of all 0s if there is none passed
    if not x0:
        x=np.zeros_like(b)
    else:
        x=np.array(x0, dtype=float)
    #check for algorithm
    if alg.strip().lower() not in ('seidel', 'jacobi'):
        raise ValueError("enter valid algorithm (seidel or jacobi)")
    n=len(A)
    #check dimensions of A and b
    if A.shape[1]!=n:
        raise ValueError("A is not square, has {n} rows and {A.shape[1]} columns")
    dimb=len(b.shape)
    if dimb!=1:
        raise ValueError("b has {dimb} dimensions, should be 1")
   
    identity=np.eye(n)

    A_diag=np.diag(1.0/np.diag(A))

    #calculation of the normalized matrices
    A_star=np.dot(A_diag,A)

    b_star=np.dot(A_diag,b)
    
    A_s=A_star-identity

    max_iter=100

    N=0
    eps_a=2*tol
    if alg.strip().lower()=="seidel":
        while (N<max_iter and eps_a > tol):
            x_old=x.copy()
            for i,A_row in enumerate (A_star):
                x[i]=b_star[i]-np.dot(A_row[:i],x[:i])-np.dot(A_row[i+1:],x[i+1:])
            N+=1
            dx=x-x_old
            eps_a=np.linalg.norm(dx)/np.linalg.norm(x)

    else:
         while (N<max_iter and eps_a > tol):
            x_old=x.copy()
            x=b_star-A_s@x
            N+=1
            dx=x-x_old
            eps_a=np.linalg.norm(dx)/np.linalg.norm(x)
    if (N>max_iter):
        raise RuntimeWarning("The method did not converge within the maximum number of iterations.")
    return x
    
def spline_function(xd,yd,order=3):
    """
    Description of function.
        Parameters
        xd: x data (array-like)
        yd: y data (array-like)
        order: order of interpolation (int)
        ----------
        Returns
        s1, s2, s3: function of interpolation  
        -------
    """
    #check if dimensions of data match
    if len(xd)!=len(yd):
        raise ValueError ("Data dimensions not equal")
    xd_unique=np.unique(xd)
    if len(xd_unique)!=len(xd):
        raise ValueError ("Repetition of values in x data")
    #sorting x values
    k_sort=np.argsort(xd)
    xd=np.array([xd[k] for k in k_sort])
    yd=np.array([yd[k] for k in k_sort])
    N=len(xd)
    a=yd[:-1]
    dy=np.diff(yd)
    dx=np.diff(xd)
    f1=dy/dx
    #first order spline
    if order==1: 
        b=f1
        def s1(x):
            k=(0 if x <= xd[0]
               else len(a)-1 if x>=xd[-1]
               else np.nonzero(xd<x)[0][-1])
            return a[k]+b[k]*(x-xd[k])
        return s1
    #second order spline
    elif order==2:
        A0=np.hstack([np.diag(dx[:-1]),np.zeros((N-2,1))])
        A1=np.hstack([np.zeros((N-2,1)),np.diag(dx[1:])])
        A=np.vstack([np.zeros((1,N-1)), A0+A1])
        A[0,:2]=[1,-1]
        B=np.zeros_like(dx)
        B[1:]=np.diff(f1)
        c=np.linalg.solve(A,B)
        b=f1-c*dx
        def s2(x):
            k=(0 if x <= xd[0]
               else len(a)-1 if x>=xd[-1]
               else np.nonzero(xd<x)[0][-1])
            return a[k]+b[k]*(x-xd[k])+c[k]*(x-xd[k])**2
        return s2
    #third order spline
    elif order==3:
        A=np.zeros((N,N))
        A[1:-1,1:-1]+=np.diag(2*(dx[:-1]+dx[1:]))
        A[1:-1,:-2]+= np.diag(dx[:-1])
        A[1:-1,2:]+=np.diag(dx[1:])
        A[0,:3]+=[-dx[1],dx[0]+dx[1],-dx[0]]
        A[-1,-3:]+=[-dx[-1],dx[-1]+dx[-2],-dx[-2]]

        B=np.zeros(N)
        B[1:-1]=3*np.diff(f1)

        c=gauss_iter_solve(A,B)
        d=np.diff(c)/(3.0*dx)
        b=f1-c[:-1]*dx-d*dx**2
        def s3(x):
            k=(0 if x <= xd[0]
               else len(a)-1 if x>=xd[-1]
               else np.nonzero(xd<x)[0][-1])
            return a[k]+b[k]*(x-xd[k])+c[k]*(x-xd[k])**2+d[k]*(x-xd[k])**3
        return s3
        
    else:
        return ValueError ("Invalid order, needs to be 1,2 or 3")
